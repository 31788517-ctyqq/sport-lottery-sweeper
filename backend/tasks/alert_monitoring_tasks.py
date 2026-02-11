"""
告警监控任务
定期执行爬虫监控检查和处理告警
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from celery import shared_task
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..services.crawler_alert_service import CrawlerAlertService
from ..services.crawler_service import CrawlerService
from ..models.crawler_config import CrawlerConfig
from ..models.crawler_logs import CrawlerTaskLog
from ..core.cache_manager import HybridCache as CacheManager

logger = logging.getLogger(__name__)


@shared_task(name="tasks.alert_monitoring.check_crawler_alerts")
def check_crawler_alerts():
    """定期检查爬虫告警"""
    logger.info("开始执行爬虫告警检查任务")
    
    try:
        db = SessionLocal()
        alert_service = CrawlerAlertService(db)
        
        # 执行告警检查
        result = alert_service.check_alerts()
        
        if result["success"]:
            logger.info(f"告警检查完成: {result['message']}")
            
            # 如果有触发的告警，记录详细日志
            if result["triggered_count"] > 0:
                logger.warning(f"检测到 {result['triggered_count']} 个告警触发")
                for alert in result["alerts"]:
                    logger.warning(f"告警: {alert['message']}")
        else:
            logger.error(f"告警检查失败: {result['message']}")
        
        db.close()
        return result
        
    except Exception as e:
        logger.error(f"告警检查任务执行失败: {str(e)}")
        if 'db' in locals():
            db.close()
        raise


@shared_task(name="tasks.alert_monitoring.collect_crawler_metrics")
def collect_crawler_metrics():
    """收集爬虫运行时指标"""
    logger.info("开始收集爬虫运行时指标")
    
    try:
        db = SessionLocal()
        cache = CacheManager()
        
        # 获取所有活跃的爬虫配置
        sources = db.query(CrawlerConfig).filter(
            CrawlerConfig.is_active == True
        ).all()
        
        collected_count = 0
        
        for source in sources:
            try:
                # 收集过去1小时的错误率指标
                error_rate = calculate_source_error_rate(db, source.id, hours=1)
                if error_rate is not None:
                    alert_service = CrawlerAlertService(db)
                    alert_service.record_metric(
                        source_id=source.id,
                        metric_type="error_rate",
                        metric_value=error_rate,
                        tags={"source_name": source.name, "time_window": "1h"}
                    )
                    collected_count += 1
                
                # 收集响应时间指标
                avg_response_time = calculate_avg_response_time(db, source.id, hours=1)
                if avg_response_time is not None:
                    alert_service = CrawlerAlertService(db)
                    alert_service.record_metric(
                        source_id=source.id,
                        metric_type="response_time",
                        metric_value=avg_response_time,
                        tags={"source_name": source.name, "time_window": "1h"}
                    )
                    collected_count += 1
                
                # 收集连续失败次数
                consecutive_failures = get_consecutive_failures(db, source.id)
                if consecutive_failures is not None:
                    alert_service = CrawlerAlertService(db)
                    alert_service.record_metric(
                        source_id=source.id,
                        metric_type="consecutive_failures",
                        metric_value=float(consecutive_failures),
                        tags={"source_name": source.name}
                    )
                    collected_count += 1
                
            except Exception as e:
                logger.error(f"收集数据源 {source.id} 指标失败: {str(e)}")
                continue
        
        logger.info(f"指标收集完成，共收集 {collected_count} 个指标")
        db.close()
        return {"success": True, "collected_metrics": collected_count}
        
    except Exception as e:
        logger.error(f"指标收集任务执行失败: {str(e)}")
        if 'db' in locals():
            db.close()
        raise


@shared_task(name="tasks.alert_monitoring.cleanup_old_alert_records")
def cleanup_old_alert_records(days_to_keep: int = 30):
    """清理旧的告警记录"""
    logger.info(f"开始清理 {days_to_keep} 天前的告警记录")
    
    try:
        db = SessionLocal()
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # 删除已解决的旧告警记录
        deleted_count = db.query(CrawlerAlertRecord).filter(
            and_(
                CrawlerAlertRecord.status == "resolved",
                CrawlerAlertRecord.resolved_at < cutoff_date
            )
        ).delete()
        
        db.commit()
        
        logger.info(f"清理完成，删除了 {deleted_count} 条旧告警记录")
        db.close()
        
        return {"success": True, "deleted_count": deleted_count}
        
    except Exception as e:
        logger.error(f"清理告警记录任务执行失败: {str(e)}")
        if 'db' in locals():
            db.rollback()
            db.close()
        raise


@shared_task(name="tasks.alert_monitoring.generate_daily_alert_report")
def generate_daily_alert_report():
    """生成每日告警报告"""
    logger.info("开始生成每日告警报告")
    
    try:
        db = SessionLocal()
        alert_service = CrawlerAlertService(db)
        
        # 获取昨天的告警统计
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        yesterday_start = datetime.combine(yesterday, datetime.min.time())
        yesterday_end = datetime.combine(yesterday, datetime.max.time())
        
        # 查询昨天的告警记录
        daily_alerts = db.query(CrawlerAlertRecord).filter(
            and_(
                CrawlerAlertRecord.triggered_at >= yesterday_start,
                CrawlerAlertRecord.triggered_at <= yesterday_end
            )
        ).all()
        
        # 统计分析
        total_alerts = len(daily_alerts)
        active_alerts = len([a for a in daily_alerts if a.status == "active"])
        resolved_alerts = len([a for a in daily_alerts if a.status == "resolved"])
        
        # 按级别统计
        alerts_by_level = {}
        for alert in daily_alerts:
            level = alert.alert_level
            alerts_by_level[level] = alerts_by_level.get(level, 0) + 1
        
        # 按数据源统计
        alerts_by_source = {}
        for alert in daily_alerts:
            if alert.source_id:
                source_id = alert.source_id
                alerts_by_source[source_id] = alerts_by_source.get(source_id, 0) + 1
        
        # 生成报告内容
        report_content = f"""
=== 爬虫系统每日告警报告 ===
报告日期: {yesterday.strftime('%Y-%m-%d')}
生成时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

总体统计:
- 总告警数: {total_alerts}
- 活跃告警: {active_alerts}
- 已解决告警: {resolved_alerts}

告警级别分布:
"""
        
        for level, count in alerts_by_level.items():
            report_content += f"- {level}: {count}\n"
        
        report_content += "\n数据源告警排行:\n"
        
        # 获取数据源名称
        source_names = {}
        sources = db.query(CrawlerConfig).all()
        for source in sources:
            source_names[source.id] = source.name
        
        # 排序显示告警最多的数据源
        sorted_sources = sorted(alerts_by_source.items(), key=lambda x: x[1], reverse=True)
        for source_id, count in sorted_sources[:10]:  # 显示前10个
            source_name = source_names.get(source_id, f"未知数据源({source_id})")
            report_content += f"- {source_name}: {count} 次告警\n"
        
        # 获取最严重的问题
        critical_alerts = [a for a in daily_alerts if a.alert_level == "critical"]
        if critical_alerts:
            report_content += f"\n严重告警详情 ({len(critical_alerts)} 个):\n"
            for alert in critical_alerts[:5]:  # 显示前5个
                report_content += f"- {alert.message} (时间: {alert.triggered_at})\n"
        
        # TODO: 发送报告邮件或保存到文件
        logger.info(f"每日告警报告生成完成:\n{report_content}")
        
        db.close()
        return {
            "success": True,
            "report_date": yesterday.isoformat(),
            "total_alerts": total_alerts,
            "report_content": report_content
        }
        
    except Exception as e:
        logger.error(f"生成每日告警报告失败: {str(e)}")
        if 'db' in locals():
            db.close()
        raise


def calculate_source_error_rate(db: Session, source_id: int, hours: int = 1) -> Optional[float]:
    """计算数据源的错误率"""
    try:
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        logs = db.query(CrawlerTaskLog).filter(
            and_(
                CrawlerTaskLog.source_id == source_id,
                CrawlerTaskLog.started_at >= start_time
            )
        ).all()
        
        if not logs:
            return None
        
        total_requests = len(logs)
        failed_requests = len([log for log in logs if log.status == 'failed'])
        
        return (failed_requests / total_requests) * 100 if total_requests > 0 else 0
        
    except Exception as e:
        logger.error(f"计算数据源 {source_id} 错误率失败: {str(e)}")
        return None


def calculate_avg_response_time(db: Session, source_id: int, hours: int = 1) -> Optional[float]:
    """计算数据源的平均响应时间"""
    try:
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        logs = db.query(CrawlerTaskLog).filter(
            and_(
                CrawlerTaskLog.source_id == source_id,
                CrawlerTaskLog.started_at >= start_time,
                CrawlerTaskLog.response_time_ms.isnot(None)
            )
        ).all()
        
        if not logs:
            return None
        
        response_times = [log.response_time_ms for log in logs if log.response_time_ms]
        return sum(response_times) / len(response_times) if response_times else None
        
    except Exception as e:
        logger.error(f"计算数据源 {source_id} 平均响应时间失败: {str(e)}")
        return None


def get_consecutive_failures(db: Session, source_id: int) -> Optional[int]:
    """获取连续失败次数"""
    try:
        # 获取最近的失败记录
        recent_failures = db.query(CrawlerTaskLog).filter(
            and_(
                CrawlerTaskLog.source_id == source_id,
                CrawlerTaskLog.status == 'failed'
            )
        ).order_by(CrawlerTaskLog.started_at.desc()).limit(20).all()
        
        if not recent_failures:
            return 0
        
        # 计算连续失败
        consecutive_count = 0
        max_consecutive = 0
        
        for log in recent_failures:
            if log.status == 'failed':
                consecutive_count += 1
                max_consecutive = max(max_consecutive, consecutive_count)
            else:
                consecutive_count = 0
        
        return max_consecutive
        
    except Exception as e:
        logger.error(f"获取数据源 {source_id} 连续失败次数失败: {str(e)}")
        return None