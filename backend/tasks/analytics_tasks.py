"""
数据分析和统计任务
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from celery import Task, shared_task
from backend.tasks import DatabaseTask, celery_app
from backend.services.analytics_service import AnalyticsService
from backend.services.match_service import MatchService
from backend.services.intelligence_service import IntelligenceService


class AnalyticsTask(Task):
    def __init__(self):
        self.analytics_service = AnalyticsService()
        self.match_service = MatchService()
        self.intelligence_service = IntelligenceService()


@celery_app.task(base=AnalyticsTask, bind=True)
def perform_analysis(self, data):
    """执行分析任务"""
    result = self.analytics_service.analyze(data)
    return result


logger = logging.getLogger(__name__)

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.analytics_tasks.generate_daily_analytics")
def generate_daily_analytics(self):
    """
    生成每日分析报告任务
    
    每天执行一次，生成前一天的统计分析报告
    """
    logger.info("开始生成每日分析报告")
    
    try:
        db = self.db
        analytics_service = AnalyticsService(db)
        match_service = MatchService(db)
        intelligence_service = IntelligenceService(db)
        
        # 计算日期范围（昨天）
        yesterday = datetime.utcnow() - timedelta(days=1)
        start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # 生成比赛统计
        match_stats = match_service.get_match_stats_by_date(start_date, end_date)
        
        # 生成情报统计
        intelligence_stats = intelligence_service.get_intelligence_stats_by_date(start_date, end_date)
        
        # 生成用户活跃统计
        user_activity_stats = analytics_service.get_user_activity_stats(start_date, end_date)
        
        # 生成系统性能统计
        system_performance_stats = analytics_service.get_system_performance_stats(start_date, end_date)
        
        # 生成综合报告
        report = analytics_service.generate_daily_report(
            date=yesterday.date(),
            match_stats=match_stats,
            intelligence_stats=intelligence_stats,
            user_activity_stats=user_activity_stats,
            system_performance_stats=system_performance_stats
        )
        
        # 保存报告到数据库
        report_id = analytics_service.save_daily_report(report)
        
        logger.info(f"每日分析报告生成完成: 日期={yesterday.date()}, 报告ID={report_id}")
        
        return {
            "success": True,
            "message": "每日分析报告生成完成",
            "date": yesterday.date().isoformat(),
            "report_id": report_id,
            "stats": {
                "matches": match_stats.get("total_matches", 0),
                "intelligence": intelligence_stats.get("total_items", 0),
                "user_activities": user_activity_stats.get("total_activities", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"每日分析报告生成任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "date": (datetime.utcnow() - timedelta(days=1)).date().isoformat()
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.analytics_tasks.generate_weekly_report")
def generate_weekly_report(self):
    """
    生成每周分析报告任务
    
    每周一执行，生成上周的统计分析报告
    """
    logger.info("开始生成每周分析报告")
    
    try:
        db = self.db
        analytics_service = AnalyticsService(db)
        
        # 计算日期范围（上周）
        today = datetime.utcnow()
        last_week_start = today - timedelta(days=today.weekday() + 7)
        last_week_end = last_week_start + timedelta(days=6)
        
        last_week_start = last_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        last_week_end = last_week_end.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # 生成每周报告
        report = analytics_service.generate_weekly_report(last_week_start, last_week_end)
        
        # 保存报告到数据库
        report_id = analytics_service.save_weekly_report(report)
        
        logger.info(f"每周分析报告生成完成: 周期={last_week_start.date()} 至 {last_week_end.date()}, 报告ID={report_id}")
        
        return {
            "success": True,
            "message": "每周分析报告生成完成",
            "period_start": last_week_start.date().isoformat(),
            "period_end": last_week_end.date().isoformat(),
            "report_id": report_id
        }
        
    except Exception as e:
        logger.error(f"每周分析报告生成任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}"
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.analytics_tasks.analyze_trends")
def analyze_trends(self, days_back: int = 30):
    """
    分析趋势任务
    
    分析指定时间范围内的数据趋势
    
    Args:
        days_back: 分析多少天内的数据
    """
    logger.info(f"开始分析数据趋势，最近{days_back}天")
    
    try:
        db = self.db
        analytics_service = AnalyticsService(db)
        
        # 计算日期范围
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        # 分析比赛趋势
        match_trends = analytics_service.analyze_match_trends(start_date, end_date)
        
        # 分析情报趋势
        intelligence_trends = analytics_service.analyze_intelligence_trends(start_date, end_date)
        
        # 分析用户行为趋势
        user_trends = analytics_service.analyze_user_behavior_trends(start_date, end_date)
        
        # 生成趋势报告
        trends_report = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days_back
            },
            "match_trends": match_trends,
            "intelligence_trends": intelligence_trends,
            "user_trends": user_trends,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # 保存趋势分析
        analytics_service.save_trends_analysis(trends_report)
        
        logger.info(f"数据趋势分析完成: 天数={days_back}")
        
        return {
            "success": True,
            "message": "数据趋势分析完成",
            "trends_report": {
                "match_trends_keys": list(match_trends.keys()),
                "intelligence_trends_keys": list(intelligence_trends.keys()),
                "user_trends_keys": list(user_trends.keys())
            }
        }
        
    except Exception as e:
        logger.error(f"数据趋势分析任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}"
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.analytics_tasks.calculate_prediction_accuracy")
def calculate_prediction_accuracy(self, days_back: int = 7):
    """
    计算预测准确率任务
    
    计算过去一段时间内预测的准确率
    
    Args:
        days_back: 计算多少天内的准确率
    """
    logger.info(f"开始计算预测准确率，最近{days_back}天")
    
    try:
        db = self.db
        analytics_service = AnalyticsService(db)
        
        # 计算日期范围
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        # 计算预测准确率
        accuracy_stats = analytics_service.calculate_prediction_accuracy(start_date, end_date)
        
        logger.info(f"预测准确率计算完成: 准确率={accuracy_stats.get('overall_accuracy', 0):.2%}")
        
        return {
            "success": True,
            "message": "预测准确率计算完成",
            "accuracy_stats": accuracy_stats
        }
        
    except Exception as e:
        logger.error(f"预测准确率计算任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "accuracy_stats": {
                "overall_accuracy": 0,
                "total_predictions": 0,
                "correct_predictions": 0
            }
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.analytics_tasks.cleanup_old_data")
def cleanup_old_data(self, days_to_keep: int = 90):
    """
    清理旧数据任务
    
    清理指定天数之前的旧数据
    
    Args:
        days_to_keep: 保留多少天内的数据
    """
    logger.info(f"开始清理旧数据，保留最近{days_to_keep}天的数据")
    
    try:
        db = self.db
        analytics_service = AnalyticsService(db)
        
        # 计算截止日期
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # 清理旧数据
        cleanup_stats = analytics_service.cleanup_old_data(cutoff_date)
        
        logger.info(f"旧数据清理完成: 清理记录={cleanup_stats.get('total_deleted', 0)}")
        
        return {
            "success": True,
            "message": "旧数据清理完成",
            "cutoff_date": cutoff_date.isoformat(),
            "cleanup_stats": cleanup_stats
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"旧数据清理任务失败: {str(e)}")
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "cleanup_stats": {
                "total_deleted": 0,
                "errors": 1
            }
        }

@shared_task(base=DatabaseTask, bind=True, name="app.tasks.analytics_tasks.check_system_health")
def check_system_health(self):
    """
    检查系统健康状态任务
    
    定期检查系统各项服务的健康状态
    """
    logger.info("开始检查系统健康状态")
    
    try:
        db = self.db
        analytics_service = AnalyticsService(db)
        
        # 检查数据库连接
        db_health = analytics_service.check_database_health()
        
        # 检查Redis连接
        redis_health = analytics_service.check_redis_health()
        
        # 检查外部API连接
        api_health = analytics_service.check_external_api_health()
        
        # 检查磁盘空间
        disk_health = analytics_service.check_disk_health()
        
        # 检查任务队列
        queue_health = analytics_service.check_queue_health()
        
        # 生成健康报告
        health_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "database": db_health,
            "redis": redis_health,
            "external_apis": api_health,
            "disk": disk_health,
            "queues": queue_health,
            "overall_health": all([
                db_health.get("healthy", False),
                redis_health.get("healthy", False),
                disk_health.get("healthy", False)
            ])
        }
        
        # 保存健康检查记录
        analytics_service.save_health_check(health_report)
        
        # 如果有严重问题，发送告警
        if not health_report["overall_health"]:
            from .notification_tasks import send_system_alert
            send_system_alert.delay(
                "系统健康检查失败",
                f"系统健康检查发现异常: {health_report}",
                level="error"
            )
        
        logger.info(f"系统健康检查完成: 总体健康={health_report['overall_health']}")
        
        return {
            "success": True,
            "message": "系统健康检查完成",
            "health_report": health_report
        }
        
    except Exception as e:
        logger.error(f"系统健康检查任务失败: {str(e)}")
        
        # 发送告警
        from .notification_tasks import send_system_alert
        send_system_alert.delay(
            "系统健康检查任务失败",
            f"系统健康检查任务执行失败: {str(e)}",
            level="error"
        )
        
        return {
            "success": False,
            "message": f"任务失败: {str(e)}",
            "health_report": {
                "overall_health": False,
                "error": str(e)
            }
        }