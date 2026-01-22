"""
系统健康检查API端点
包含数据库监控和连接池状态检查
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.database_monitor import db_monitor
from typing import Dict, Any
import asyncio

router = APIRouter()

@router.get("/health/database", 
           summary="数据库健康检查",
           description="检查数据库连接状态和连接池配置")
async def database_health_check() -> Dict[str, Any]:
    """
    获取数据库综合健康报告
    """
    try:
        report = db_monitor.get_comprehensive_health_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")

@router.get("/health/database/sync-pool",
           summary="同步数据库连接池状态",
           description="获取同步数据库连接的连接池详细信息")
async def sync_connection_pool_status() -> Dict[str, Any]:
    """
    获取同步数据库连接池状态
    """
    try:
        status = db_monitor.get_connection_pool_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取连接池状态失败: {str(e)}")

@router.get("/health/database/async-pool",
           summary="异步数据库连接池状态",
           description="获取异步数据库连接的连接池详细信息")
async def async_connection_pool_status() -> Dict[str, Any]:
    """
    获取异步数据库连接池状态
    """
    try:
        status = await db_monitor.get_async_connection_pool_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取异步连接池状态失败: {str(e)}")

@router.get("/health/database/statistics",
           summary="数据库统计信息",
           description="获取数据库表和记录的统计信息")
async def database_statistics() -> Dict[str, Any]:
    """
    获取数据库统计信息
    """
    try:
        stats = db_monitor.get_database_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据库统计失败: {str(e)}")

@router.get("/health/database/config",
           summary="数据库配置信息",
           description="获取当前数据库连接池配置参数")
async def database_configuration() -> Dict[str, Any]:
    """
    获取数据库配置信息
    """
    from backend.config import settings
    
    config_info = {
        "database_url": settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL,
        "async_database_url": settings.ASYNC_DATABASE_URL.split('@')[-1] if '@' in settings.ASYNC_DATABASE_URL else settings.ASYNC_DATABASE_URL,
        "database_type": "sqlite" if settings.DATABASE_URL.startswith("sqlite") else "postgresql" if settings.DATABASE_URL.startswith("postgresql") else "mysql" if settings.DATABASE_URL.startswith("mysql") else "unknown",
        "pool_settings": {
            "db_pool_size": settings.DB_POOL_SIZE,
            "db_max_overflow": settings.DB_MAX_OVERFLOW,
            "db_pool_timeout": settings.DB_POOL_TIMEOUT,
            "db_pool_recycle": settings.DB_POOL_RECYCLE,
            "db_pool_pre_ping": settings.DB_POOL_PRE_PING,
            "database_echo": settings.DATABASE_ECHO
        },
        "async_pool_settings": {
            "async_db_pool_size": settings.ASYNC_DB_POOL_SIZE,
            "async_db_max_overflow": settings.ASYNC_DB_MAX_OVERFLOW,
            "async_db_pool_timeout": settings.ASYNC_DB_POOL_TIMEOUT,
            "async_db_pool_recycle": settings.ASYNC_DB_POOL_RECYCLE
        },
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }
    
    return config_info

@router.get("/health",
           summary="系统总体健康状态",
           description="获取系统总体健康状态（包含数据库）")
async def overall_health() -> Dict[str, Any]:
    """
    获取系统总体健康状态
    """
    try:
        db_health = db_monitor.get_comprehensive_health_report()
        
        overall_status = db_health["status"]
        overall_score = db_health["overall_health_score"]
        
        return {
            "status": overall_status,
            "health_score": overall_score,
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "components": {
                "database": db_health
            },
            "version": "0.1.0",
            "service": "Sport Lottery Sweeper System"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"系统健康检查失败: {str(e)}")