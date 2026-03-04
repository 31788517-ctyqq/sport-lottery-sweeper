from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
from datetime import datetime, timedelta
import psutil  # 用于系统资源监控
import time

from backend.database import get_db
from backend.models.crawler_tasks import CrawlerTask
from backend.models.crawler_source_stats import CrawlerSourceStat
from backend.models.data_sources import DataSource

router = APIRouter(prefix="/crawler/monitor", tags=["crawler-monitor"])

@router.get("/health")
async def get_system_health(
    db: Session = Depends(get_db)
):
    """
    获取系统健康状态
    """
    try:
        # 获取系统健康指标
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')
        
        # 获取爬虫任务统计
        total_sources = db.query(DataSource).count()
        active_sources = db.query(DataSource).filter(DataSource.status == True).count()
        total_tasks = db.query(CrawlerTask).count()
        running_tasks = db.query(CrawlerTask).filter(CrawlerTask.status == 'RUNNING').count()
        
        health_status = {
            "overall": "healthy",  # overall health status
            "systemHealth": {
                "cpu": {"usage": cpu_percent, "status": "normal"},
                "memory": {"usage": memory_info.percent, "status": "normal"},
                "disk": {"usage": disk_usage.percent, "status": "normal"},
                "network": {"status": "connected"}
            },
            "crawlerHealth": {
                "totalSources": total_sources,
                "activeSources": active_sources,
                "totalTasks": total_tasks,
                "runningTasks": running_tasks,
                "successRate": 96.2,
                "dataQuality": 94.8,
                "responsePerformance": 87.3
            },
            "lastCheck": datetime.utcnow().isoformat()
        }
        
        return {
            "code": 200,
            "data": health_status,
            "message": "系统健康状态获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources")
async def get_system_resources(
    db: Session = Depends(get_db)
):
    """
    获取系统资源使用情况
    """
    try:
        # 获取系统资源信息
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')
        
        # 模拟数据库连接数
        db_connections = 24
        db_max_connections = 100
        
        resources = {
            "cpu": round(cpu_percent, 1),
            "memory": round(memory_info.percent, 1),
            "disk": round(disk_usage.percent, 1),
            "dbConnections": db_connections,
            "dbMaxConnections": db_max_connections,
            "timestamp": int(time.time() * 1000)
        }
        
        return {
            "code": 200,
            "data": resources,
            "message": "系统资源获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_alerts(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, description="active, acknowledged, resolved"),
    db: Session = Depends(get_db)
):
    """
    获取告警列表
    """
    try:
        # 模拟一些告警数据
        alerts = [
            {
                "id": 1,
                "severity": "critical",
                "metric_name": "数据源连接失败",
                "message": "数据源API连续5分钟无响应",
                "current_value": 0,
                "threshold": 1,
                "triggered_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                "status": "active"
            },
            {
                "id": 2,
                "severity": "warning",
                "metric_name": "采集成功率下降",
                "message": "采集成功率降至85%以下",
                "current_value": 82.5,
                "threshold": 85.0,
                "triggered_at": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
                "status": "active"
            },
            {
                "id": 3,
                "severity": "info",
                "metric_name": "数据量激增",
                "message": "数据采集量较平时增加50%",
                "current_value": 150,
                "threshold": 100,
                "triggered_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "status": "active"
            },
            {
                "id": 4,
                "severity": "warning",
                "metric_name": "响应时间过长",
                "message": "平均响应时间超过3秒",
                "current_value": 3.2,
                "threshold": 3.0,
                "triggered_at": (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
                "status": "active"
            }
        ]
        
        # 分页
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paged_alerts = alerts[start_idx:end_idx]
        
        return {
            "code": 200,
            "data": {
                "items": paged_alerts,
                "total": len(alerts),
                "page": page,
                "size": size,
                "pages": (len(alerts) + size - 1) // size
            },
            "message": "告警信息获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """
    确认告警
    """
    try:
        # 这里应该是更新告警状态的逻辑
        # 模拟确认操作
        return {
            "code": 200,
            "data": {"id": alert_id, "status": "acknowledged"},
            "message": "告警已确认"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics(
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取监控指标数据
    """
    try:
        # 模拟指标数据
        metrics = {
            "totalRequests": 12500,
            "successRate": 96.2,
            "avgResponseTime": 280.5,
            "dataQualityScore": 94.8,
            "uptime": 99.9,
            "lastUpdated": datetime.utcnow().isoformat()
        }
        
        return {
            "code": 200,
            "data": metrics,
            "message": "监控指标获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends/success-rate")
async def get_success_rate_trend(
    range_hours: int = Query(24, description="小时范围"),
    db: Session = Depends(get_db)
):
    """
    获取采集成功率趋势
    """
    try:
        # 生成模拟的成功率趋势数据
        trends = []
        for i in range(range_hours):
            time_point = datetime.utcnow() - timedelta(hours=range_hours-i)
            success_rate = 95.0 + (i % 5) - 2.5  # 模拟波动
            volume = 500 + (i % 10) * 20  # 模拟数据量波动
            
            trends.append({
                "timestamp": time_point.isoformat(),
                "successRate": round(success_rate, 2),
                "volume": volume
            })
        
        return {
            "code": 200,
            "data": trends,
            "message": "成功率趋势获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/data-volume")
async def get_data_volume_stats(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取数据采集量统计
    """
    try:
        # 模拟数据采集量统计
        stats = [
            {"name": "比赛数据", "value": 335},
            {"name": "球员信息", "value": 310},
            {"name": "球队信息", "value": 234},
            {"name": "赔率数据", "value": 135},
            {"name": "新闻资讯", "value": 154}
        ]
        
        return {
            "code": 200,
            "data": stats,
            "message": "数据采集量统计获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/instances")
async def get_crawler_instances(
    db: Session = Depends(get_db)
):
    """
    获取爬虫实例状态
    """
    try:
        instances = [
            {
                "id": 1,
                "name": "crawler-instance-1",
                "status": "running",
                "cpuUsage": 23.5,
                "memoryUsage": 45.2,
                "tasksRunning": 3,
                "lastHeartbeat": (datetime.utcnow() - timedelta(seconds=10)).isoformat()
            },
            {
                "id": 2,
                "name": "crawler-instance-2",
                "status": "idle",
                "cpuUsage": 5.2,
                "memoryUsage": 32.1,
                "tasksRunning": 0,
                "lastHeartbeat": (datetime.utcnow() - timedelta(seconds=30)).isoformat()
            }
        ]
        
        return {
            "code": 200,
            "data": instances,
            "message": "爬虫实例状态获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/database/metrics")
async def get_database_metrics(
    db: Session = Depends(get_db)
):
    """
    获取数据库性能指标
    """
    try:
        metrics = {
            "connections": 24,
            "maxConnections": 100,
            "activeQueries": 3,
            "slowQueries": 2,
            "cacheHitRatio": 95.6,
            "bufferCacheHit": 98.2,
            "lastUpdated": datetime.utcnow().isoformat()
        }
        
        return {
            "code": 200,
            "data": metrics,
            "message": "数据库性能指标获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network/status")
async def get_network_status(
    db: Session = Depends(get_db)
):
    """
    获取网络连接状态
    """
    try:
        status = {
            "connectivity": "connected",
            "latency": 12.5,
            "bandwidth": "100Mbps",
            "packetLoss": 0.1,
            "lastChecked": datetime.utcnow().isoformat()
        }
        
        return {
            "code": 200,
            "data": status,
            "message": "网络连接状态获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))