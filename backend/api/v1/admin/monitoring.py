"""
监控管理API
提供系统监控、健康状态等功能
"""
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

router = APIRouter()

@router.get("/monitor/system-stats")
async def get_system_stats(
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
        
        # 获取爬虫任务统计
        total_sources = db.query(DataSource).count()
        active_sources = db.query(DataSource).filter(DataSource.status == True).count()
        
        # 获取最近24小时的指标数据（模拟）
        now = datetime.utcnow()
        start_time = now - timedelta(hours=24)
        
        # 返回系统统计信息
        stats = {
            "cpuPercent": cpu_percent,
            "memoryPercent": memory_info.percent,
            "diskPercent": disk_usage.percent,
            "totalSources": total_sources,
            "activeSources": active_sources,
            "timestamp": int(time.time() * 1000)  # 毫秒时间戳
        }
        
        return {
            "success": True,
            "data": stats,
            "message": "系统统计获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitor/crawler-metrics")
async def get_crawler_metrics(
    hours: int = Query(24, description="获取过去多少小时的数据"),
    db: Session = Depends(get_db)
):
    """
    获取爬虫指标数据（成功率、响应时间等）
    """
    try:
        # 计算时间范围
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # 获取指标数据（模拟）
        # 在实际实现中，这应该从CrawlerMetric表中查询
        metrics = []
        for i in range(0, hours*2):  # 每30分钟一个点
            time_point = start_time + timedelta(minutes=i*30)
            metric = {
                "timestamp": time_point.isoformat(),
                "successRate": round(95.0 + (i % 5) - 2.5, 2),  # 模拟成功率波动
                "avgResponseTime": round(300 + (i % 10) * 10, 2),  # 模拟响应时间波动
                "requestsCount": 50 + (i % 20)  # 模拟请求数量
            }
            metrics.append(metric)
        
        return {
            "success": True,
            "data": {
                "metrics": metrics,
                "summary": {
                    "totalRequests": sum([m["requestsCount"] for m in metrics]),
                    "averageSuccessRate": round(sum([m["successRate"] for m in metrics]) / len(metrics), 2),
                    "averageResponseTime": round(sum([m["avgResponseTime"] for m in metrics]) / len(metrics), 2)
                }
            },
            "message": "爬虫指标获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitor/alerts")
async def get_monitoring_alerts(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, description="alert, warning, resolved"),
    db: Session = Depends(get_db)
):
    """
    获取监控告警信息
    """
    try:
        # 这里应该是查询告警记录表
        # 模拟一些告警数据
        alerts = [
            {
                "id": 1,
                "title": "数据源连接超时",
                "level": "warning",
                "message": "数据源API响应时间超过阈值",
                "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                "status": "active"
            },
            {
                "id": 2,
                "title": "IP被封禁",
                "level": "alert",
                "message": "检测到IP地址被目标站点封禁",
                "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
                "status": "active"
            }
        ]
        
        # 分页
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paged_alerts = alerts[start_idx:end_idx]
        
        return {
            "success": True,
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


@router.get("/monitor/data-center-stats")
async def get_data_center_stats(
    db: Session = Depends(get_db)
):
    """
    获取数据中心统计信息
    """
    try:
        # 这里应该是查询数据相关的统计
        # 模拟数据统计
        stats = {
            "totalRecords": 12580,
            "todayRecords": 320,
            "successRate": 96.5,
            "avgUpdateTime": "2026-01-22T10:30:00Z",
            "dataSources": 8,
            "activeTasks": 5
        }
        
        return {
            "success": True,
            "data": stats,
            "message": "数据中心统计获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))