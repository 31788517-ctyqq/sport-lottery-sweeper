"""
监控仪表板API接口
提供爬虫系统监控数据的可视化接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from ...database import get_db
from ...services.crawler_alert_service import CrawlerAlertService
from ...services.enhanced_crawler_service import EnhancedCrawlerService
from ...models.crawler_config import CrawlerConfig
from ...models.crawler_logs import CrawlerTaskLog, CrawlerSourceStat
from ...models.crawler_alert_records import CrawlerAlertRecord
from ...models.crawler_alert_rules import CrawlerAlertRule
from ...core.auth import get_current_user
from ...models.admin_user import AdminUser
from ...schemas.crawler_monitoring import MonitoringOverview, SourcePerformance, AlertTrends, RealtimeMetrics, TopIssues

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring-dashboard"])


@router.get("/dashboard/overview", response_model=dict)
async def get_monitoring_overview(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """获取监控概览数据"""
    try:
        alert_service = CrawlerAlertService(db)
        enhanced_service = EnhancedCrawlerService(db)
        
        # 获取告警统计
        alert_stats = alert_service.get_alert_records(limit=1000)
        total_alerts = len(alert_stats)
        active_alerts = len([a for a in alert_stats if a["status"] == "active"])
        
        # 按级别统计告警
        alerts_by_level = {}
        for alert in alert_stats:
            level = alert["alert_level"]
            alerts_by_level[level] = alerts_by_level.get(level, 0) + 1
        
        # 获取数据源健康状态
        health_status = enhanced_service.get_source_health_status()
        
        # 获取最近24小时的统计
        yesterday = datetime.utcnow() - timedelta(hours=24)
        recent_logs = db.query(CrawlerTaskLog).filter(
            CrawlerTaskLog.started_at >= yesterday
        ).all()
        
        total_requests_24h = len(recent_logs)
        failed_requests_24h = len([log for log in recent_logs if log.status == 'failed'])
        success_rate_24h = ((total_requests_24h - failed_requests_24h) / total_requests_24h * 100) if total_requests_24h > 0 else 0
        
        # 计算平均响应时间
        response_times = [log.response_time_ms for log in recent_logs if log.response_time_ms]
        avg_response_time_24h = sum(response_times) / len(response_times) if response_times else 0
        
        overview = {
            "timestamp": datetime.utcnow().isoformat(),
            "alerts": {
                "total": total_alerts,
                "active": active_alerts,
                "by_level": alerts_by_level
            },
            "sources": health_status,
            "performance_24h": {
                "total_requests": total_requests_24h,
                "failed_requests": failed_requests_24h,
                "success_rate": round(success_rate_24h, 2),
                "avg_response_time_ms": round(avg_response_time_24h, 2)
            }
        }
        
        return {
            "code": 200,
            "message": "获取监控概览成功",
            "data": overview
        }
        
    except Exception as e:
        logger.error(f"获取监控概览API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取监控概览失败: {str(e)}")


@router.get("/dashboard/source-performance", response_model=dict)
async def get_source_performance(
    hours: int = Query(24, ge=1, le=168, description="时间范围（小时）"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """获取数据源性能数据"""
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # 获取时间范围内的任务日志
        logs = db.query(CrawlerTaskLog).filter(
            and_(
                CrawlerTaskLog.started_at >= start_time,
                CrawlerTaskLog.started_at <= end_time
            )
        ).all()
        
        # 按数据源分组统计
        source_stats = {}
        
        for log in logs:
            source_id = log.source_id
            if source_id not in source_stats:
                source_stats[source_id] = {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "response_times": [],
                    "error_messages": []
                }
            
            source_stats[source_id]["total_requests"] += 1
            
            if log.status == "success":
                source_stats[source_id]["successful_requests"] += 1
            else:
                source_stats[source_id]["failed_requests"] += 1
                if log.error_message:
                    source_stats[source_id]["error_messages"].append(log.error_message)
            
            if log.response_time_ms:
                source_stats[source_id]["response_times"].append(log.response_time_ms)
        
        # 计算统计指标
        performance_data = []
        for source_id, stats in source_stats.items():
            success_rate = (stats["successful_requests"] / stats["total_requests"] * 100) if stats["total_requests"] > 0 else 0
            avg_response_time = sum(stats["response_times"]) / len(stats["response_times"]) if stats["response_times"] else 0
            
            # 获取数据源名称
            source_config = db.query(CrawlerConfig).filter(CrawlerConfig.id == source_id).first()
            source_name = source_config.name if source_config else f"Source_{source_id}"
            
            performance_data.append({
                "source_id": source_id,
                "source_name": source_name,
                "total_requests": stats["total_requests"],
                "successful_requests": stats["successful_requests"],
                "failed_requests": stats["failed_requests"],
                "success_rate": round(success_rate, 2),
                "avg_response_time_ms": round(avg_response_time, 2),
                "error_samples": stats["error_messages"][:3]  # 最多3个错误样本
            })
        
        # 按成功率排序
        performance_data.sort(key=lambda x: x["success_rate"], reverse=True)
        
        return {
            "code": 200,
            "message": "获取数据源性能数据成功",
            "data": {
                "time_range_hours": hours,
                "sources": performance_data,
                "total_sources": len(performance_data)
            }
        }
        
    except Exception as e:
        logger.error(f"获取数据源性能API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取数据源性能失败: {str(e)}")


@router.get("/dashboard/alert-trends", response_model=dict)
async def get_alert_trends(
    days: int = Query(7, ge=1, le=30, description="天数范围"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """获取告警趋势数据"""
    try:
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days-1)
        
        trends_data = []
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            day_start = datetime.combine(current_date, datetime.min.time())
            day_end = datetime.combine(current_date, datetime.max.time())
            
            # 查询当天的告警记录
            daily_alerts = db.query(CrawlerAlertRecord).filter(
                and_(
                    CrawlerAlertRecord.triggered_at >= day_start,
                    CrawlerAlertRecord.triggered_at <= day_end
                )
            ).all()
            
            # 按级别统计
            alerts_by_level = {}
            for alert in daily_alerts:
                level = alert.alert_level
                alerts_by_level[level] = alerts_by_level.get(level, 0) + 1
            
            trends_data.append({
                "date": current_date.isoformat(),
                "total_alerts": len(daily_alerts),
                "alerts_by_level": alerts_by_level,
                "active_alerts": len([a for a in daily_alerts if a.status == "active"]),
                "resolved_alerts": len([a for a in daily_alerts if a.status == "resolved"])
            })
        
        return {
            "code": 200,
            "message": "获取告警趋势数据成功",
            "data": {
                "days": days,
                "trends": trends_data
            }
        }
        
    except Exception as e:
        logger.error(f"获取告警趋势API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取告警趋势失败: {str(e)}")


@router.get("/dashboard/realtime-metrics", response_model=dict)
async def get_realtime_metrics(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """获取实时指标数据"""
    try:
        enhanced_service = EnhancedCrawlerService(db)
        
        # 获取所有数据源的实时状态
        health_status = enhanced_service.get_source_health_status()
        
        # 获取最近的告警
        recent_alerts = db.query(CrawlerAlertRecord).filter(
            CrawlerAlertRecord.status == "active"
        ).order_by(CrawlerAlertRecord.triggered_at.desc()).limit(10).all()
        
        recent_alerts_data = [
            {
                "id": alert.id,
                "rule_id": alert.rule_id,
                "alert_level": alert.alert_level,
                "message": alert.message,
                "triggered_at": alert.triggered_at.isoformat() if alert.triggered_at else None,
                "source_id": alert.source_id
            }
            for alert in recent_alerts
        ]
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "sources_health": health_status,
            "recent_active_alerts": recent_alerts_data,
            "system_status": health_status.get("overall_status", "unknown")
        }
        
        return {
            "code": 200,
            "message": "获取实时指标成功",
            "data": metrics
        }
        
    except Exception as e:
        logger.error(f"获取实时指标API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取实时指标失败: {str(e)}")


@router.get("/dashboard/top-issues", response_model=dict)
async def get_top_issues(
    limit: int = Query(10, ge=1, le=50, description="返回数量限制"),
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """获取主要问题排行"""
    try:
        # 获取失败最多的数据源
        source_failures_query = db.query(
            CrawlerTaskLog.source_id,
            CrawlerConfig.name.label("source_name"),
            db.func.count(CrawlerTaskLog.id).label("failure_count")
        ).join(
            CrawlerConfig, CrawlerTaskLog.source_id == CrawlerConfig.id
        ).filter(
            CrawlerTaskLog.status == "failed"
        ).group_by(
            CrawlerTaskLog.source_id, CrawlerConfig.name
        ).order_by(
            db.func.count(CrawlerTaskLog.id).desc()
        ).limit(limit)
        
        top_failing_sources = [
            {
                "source_id": row.source_id,
                "source_name": row.source_name,
                "failure_count": row.failure_count
            }
            for row in source_failures_query.all()
        ]
        
        # 获取最常见的错误消息
        common_errors_query = db.query(
            CrawlerTaskLog.error_message,
            db.func.count(CrawlerTaskLog.id).label("error_count")
        ).filter(
            CrawlerTaskLog.error_message.isnot(None)
        ).group_by(
            CrawlerTaskLog.error_message
        ).order_by(
            db.func.count(CrawlerTaskLog.id).desc()
        ).limit(limit)
        
        common_errors = [
            {
                "error_message": row.error_message[:100] + "..." if len(row.error_message) > 100 else row.error_message,
                "count": row.error_count
            }
            for row in common_errors_query.all()
        ]
        
        # 获取告警最多的规则
        alert_rules_query = db.query(
            CrawlerAlertRecord.rule_id,
            CrawlerAlertRule.name.label("rule_name"),
            CrawlerAlertRule.metric_type,
            db.func.count(CrawlerAlertRecord.id).label("alert_count")
        ).join(
            CrawlerAlertRule, CrawlerAlertRecord.rule_id == CrawlerAlertRule.id
        ).group_by(
            CrawlerAlertRecord.rule_id, CrawlerAlertRule.name, CrawlerAlertRule.metric_type
        ).order_by(
            db.func.count(CrawlerAlertRecord.id).desc()
        ).limit(limit)
        
        top_alert_rules = [
            {
                "rule_id": row.rule_id,
                "rule_name": row.rule_name,
                "metric_type": row.metric_type,
                "alert_count": row.alert_count
            }
            for row in alert_rules_query.all()
        ]
        
        issues = {
            "top_failing_sources": top_failing_sources,
            "common_errors": common_errors,
            "top_alert_rules": top_alert_rules
        }
        
        return {
            "code": 200,
            "message": "获取主要问题排行成功",
            "data": issues
        }
        
    except Exception as e:
        logger.error(f"获取主要问题排行API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取主要问题排行失败: {str(e)}")