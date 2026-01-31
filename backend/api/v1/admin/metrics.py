"""
监控指标API端点
提供系统性能监控、API性能监控、错误统计和健康检查等功能
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import time
import psutil
import os
from datetime import datetime

from backend.core.monitoring_middleware import MonitoringMiddleware
from backend.database import get_db
from backend.core.auth import get_current_admin_user
from backend.models.user import User

router = APIRouter()

# 全局监控中间件实例，用于获取统计数据
monitoring_mw = MonitoringMiddleware(None)

@router.get("/metrics/system")
async def get_system_metrics(current_user: User = Depends(get_current_admin_user)):
    """
    获取系统性能指标
    包括CPU使用率、内存使用率、磁盘使用率等
    """
    # CPU使用率
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # 内存信息
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    memory_available = memory.available
    
    # 磁盘信息
    disk_usage = psutil.disk_usage('/')
    disk_percent = (disk_usage.used / disk_usage.total) * 100
    
    # 进程信息
    process = psutil.Process(os.getpid())
    process_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu": {
            "percent": cpu_percent
        },
        "memory": {
            "percent": memory_percent,
            "available": memory_available,
            "used": process_memory
        },
        "disk": {
            "percent": disk_percent
        },
        "process": {
            "memory_used_mb": round(process_memory, 2),
            "uptime_seconds": time.time() - getattr(monitoring_mw, '_start_time', time.time())
        }
    }
    
    return {"code": 200, "message": "success", "data": metrics}


@router.get("/metrics/api-performance")
async def get_api_performance(current_user: User = Depends(get_current_admin_user)):
    """
    获取API性能指标
    包括请求数、错误数、平均响应时间等
    """
    metrics = {
        "request_count": getattr(monitoring_mw, 'request_count', 0),
        "error_count": getattr(monitoring_mw, 'error_count', 0),
        "total_response_time": getattr(monitoring_mw, 'total_response_time', 0.0),
        "average_response_time": (
            getattr(monitoring_mw, 'total_response_time', 0.0) / 
            max(1, getattr(monitoring_mw, 'request_count', 1))
        ),
        "error_rate": (
            getattr(monitoring_mw, 'error_count', 0) / 
            max(1, getattr(monitoring_mw, 'request_count', 1)) * 100
        )
    }
    
    return {"code": 200, "message": "success", "data": metrics}


@router.get("/metrics/errors")
async def get_error_stats(current_user: User = Depends(get_current_admin_user)):
    """
    获取错误统计信息
    """
    error_stats = {
        "total_errors": getattr(monitoring_mw, 'error_count', 0),
        "error_details": []  # 在实际实现中，这里可以包含具体的错误信息
    }
    
    return {"code": 200, "message": "success", "data": error_stats}


@router.get("/metrics/health")
async def health_check():
    """
    健康检查端点
    返回系统和服务的健康状态
    """
    # 检查各个服务的健康状况
    checks = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "healthy",
            "database": "pending",  # 实际项目中需要检查数据库连接
            "cache": "pending",     # 实际项目中需要检查缓存服务
            "message_queue": "pending"  # 实际项目中需要检查消息队列
        },
        "details": {
            "uptime": time.time() - getattr(monitoring_mw, '_start_time', time.time()),
            "version": "1.0.0"
        }
    }
    
    return {"code": 200, "message": "success", "data": checks}