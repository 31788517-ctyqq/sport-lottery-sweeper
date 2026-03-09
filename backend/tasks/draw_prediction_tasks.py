"""
平局预测相关的 Celery 定时任务
"""
from backend.celery_app import celery_app
import logging
logger = logging.getLogger(__name__)
from backend.database import SessionLocal
from backend.services.alert_service import check_and_trigger_alert
from backend.services.draw_prediction_service import get_predictions
from backend.services.poisson_11_service import scan_for_date
from backend.models.draw_prediction_result import DrawPredictionResult
from backend.models.match import Match
from datetime import datetime, timedelta



@celery_app.task
def update_prediction_results():
    """
    定时任务：基于真实比分回写预测结果
    优先使用 Match.home_score / Match.away_score
    """
    db = SessionLocal()
    try:
        start_date = datetime.utcnow() - timedelta(days=30)
        predictions = get_predictions(db, start_date=start_date)

        updated_count = 0
        unresolved_count = 0
        for pred in predictions:
            if pred.actual_result:
                continue

            match = (
                db.query(Match)
                .filter(Match.match_identifier == pred.match_id)
                .order_by(Match.id.desc())
                .first()
            )
            if not match:
                unresolved_count += 1
                continue

            if match.home_score is None or match.away_score is None:
                unresolved_count += 1
                continue

            if match.home_score == match.away_score:
                pred.actual_result = "draw"
            elif match.home_score > match.away_score:
                pred.actual_result = "home"
            else:
                pred.actual_result = "away"
            updated_count += 1

        db.commit()
        logger.debug(f"[定时任务] 更新了 {updated_count} 条预测结果，未解析 {unresolved_count} 条")

        return {
            "status": "success",
            "updated_count": updated_count,
            "unresolved_count": unresolved_count,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.debug(f"[定时任务] 更新预测结果失败: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()



@celery_app.task
def monitor_and_alert():
    """
    定时任务：监控命中率并触发告警
    建议每天执行一次
    """
    db = SessionLocal()
    try:
        alert_info = check_and_trigger_alert(db)

        if alert_info['should_alert']:
            # TODO: 实际项目中，这里应该发送邮件、短信或企业微信通知
            logger.debug(f"[告警] {alert_info['message']}")

            # 可以将告警记录到数据库，这里先打印日志
            logger.debug(f"[告警] 当前命中率: {alert_info['accuracy']:.1%}, 阈值: {alert_info['threshold']:.1%}")

        return {
            "status": "success",
            "alert_triggered": alert_info['should_alert'],
            "accuracy": alert_info.get('accuracy'),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.debug(f"[定时任务] 监控告警失败: {str(e)}")
        raise
    finally:
        db.close()


@celery_app.task
def scan_poisson_11_daily():
    """
    定时任务：对当日竞彩进行 1-1 Poisson 扫盘
    """
    db = SessionLocal()
    try:
        target_date = datetime.now().date()
        results = scan_for_date(db, target_date, data_source="yingqiu_bd", overwrite=True)
        return {
            "status": "success",
            "date": target_date.isoformat(),
            "total": len(results),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.debug(f"[定时任务] 1-1 Poisson 扫盘失败: {str(e)}")
        raise
    finally:
        db.close()


# 配置定时任务执行周期
@celery_app.on_after_configure.connect

def setup_periodic_tasks(sender, **kwargs):
    """
    设置定时任务执行周期
    """
    # 每天凌晨2点更新比赛结果
    sender.add_periodic_task(
        update_prediction_results,
        schedule=crontab(hour=2, minute=0),
        name='update_prediction_results_daily'
    )

    # 每天上午9点监控命中率
    sender.add_periodic_task(
        monitor_and_alert,
        schedule=crontab(hour=9, minute=0),
        name='monitor_accuracy_daily'
    )

    # 每天上午10点执行专抓1-1扫盘
    sender.add_periodic_task(
        scan_poisson_11_daily,
        schedule=crontab(hour=10, minute=0),
        name='poisson_11_daily_scan'
    )
    logger.debug("[Celery] 定时任务已配置")



from celery.schedules import crontab
