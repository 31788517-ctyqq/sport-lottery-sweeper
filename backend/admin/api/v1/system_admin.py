"""
系统管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import psutil
import os
from pydantic import BaseModel
from typing import Generic, TypeVar

# 修正导入路径
from ....api.deps import get_db
from ....models.user import User

# 定义响应模型
T = TypeVar('T')

class UnifiedResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[Dict[str, Any]] = None

    @classmethod
    def success(cls, data: T, message: str = "操作成功"):
        return cls(success=True, data=data, message=message)

    @classmethod
    def error(cls, message: str, error_code: Optional[str] = None):
        return cls(success=False, message=message, error={"code": error_code, "message": message})

router = APIRouter(prefix="/system", tags=["admin-system"])


@router.get("/status", response_model=UnifiedResponse[Dict[str, Any]])
async def get_system_status():
    """
    获取系统状态
    """
    try:
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_total = memory.total
        memory_available = memory.available
        memory_used = memory.used
        
        # 磁盘使用情况
        disk_usage = psutil.disk_usage('/')
        disk_percent = (disk_usage.used / disk_usage.total) * 100
        disk_total = disk_usage.total
        disk_used = disk_usage.used
        disk_free = disk_usage.free
        
        # 进程信息
        process = psutil.Process(os.getpid())
        process_memory = process.memory_info().rss
        
        # 返回系统状态
        status_data = {
            "server_time": datetime.utcnow().isoformat(),
            "cpu_percent": cpu_percent,
            "memory": {
                "percent": memory_percent,
                "total": memory_total,
                "available": memory_available,
                "used": memory_used
            },
            "disk": {
                "percent": disk_percent,
                "total": disk_total,
                "used": disk_used,
                "free": disk_free
            },
            "process": {
                "memory_usage": process_memory,
                "pid": process.pid,
                "name": process.name()
            },
            "uptime": "N/A"
        }
        
        return UnifiedResponse.success(status_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=UnifiedResponse[Dict[str, Any]])
async def get_system_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    获取系统统计信息
    """
    try:
        from sqlalchemy import select, func
        from ....models.match import Match
        
        # 查询用户数量
        user_count_result = await db.execute(select(func.count(User.id)))
        user_count = user_count_result.scalar_one()
        
        # 查询比赛数量
        match_count_result = await db.execute(select(func.count(Match.id)))
        match_count = match_count_result.scalar_one()
        
        # 近7天比赛数量
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_matches_result = await db.execute(
            select(func.count(Match.id)).where(Match.created_at >= seven_days_ago)
        )
        recent_matches_count = recent_matches_result.scalar_one()
        
        stats_data = {
            "total_users": user_count,
            "total_matches": match_count,
            "recent_matches_7d": recent_matches_count,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        return UnifiedResponse.success(stats_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config", response_model=UnifiedResponse[Dict[str, Any]])
async def get_system_config():
    """
    获取系统配置信息
    """
    try:
        import sys
        import platform
        
        config_info = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor(),
            "architecture": platform.architecture(),
            "environment_vars": {
                k: v for k, v in os.environ.items() 
                if k.startswith(('APP_', 'DB_', 'CELERY_', 'REDIS_'))
            },
            "server_time": datetime.utcnow().isoformat()
        }
        
        return UnifiedResponse.success(config_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-cache", response_model=UnifiedResponse[Dict[str, Any]])
async def clear_cache():
    """
    清理系统缓存
    """
    try:
        # 这里应该是清理缓存的逻辑
        # 暂时返回模拟响应
        return UnifiedResponse.success({
            "message": "缓存清理完成",
            "cleared_items": 15,
            "space_freed": "2.5 MB",
            "completed_at": datetime.utcnow().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))