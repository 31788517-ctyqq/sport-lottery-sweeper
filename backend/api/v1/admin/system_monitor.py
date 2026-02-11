"""
系统监控API端点
提供系统健康状态和资源使用情况的监控接口
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import psutil
import platform
from datetime import datetime, timedelta

from backend.database import get_db

# 创建路由器
router = APIRouter(tags=["system-monitor"])

@router.get("/health")
async def get_system_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    获取系统健康状态
    """
    try:
        # 从现有的health模块获取数据库健康信息
        from backend.app.api.admin.system.health import overall_health
        # 直接调用函数，不传递参数
        health_result = await overall_health()
        
        return {
            "success": True,
            "data": health_result,
            "message": "系统健康状态获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统健康状态失败: {str(e)}")

@router.get("/resources")
async def get_system_resources() -> Dict[str, Any]:
    """
    获取系统资源使用情况
    """
    try:
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used = round(memory.used / 1024 / 1024 / 1024, 2)  # GB
        memory_total = round(memory.total / 1024 / 1024 / 1024, 2)  # GB
        
        # 磁盘使用情况
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used = round(disk.used / 1024 / 1024 / 1024, 2)  # GB
        disk_total = round(disk.total / 1024 / 1024 / 1024, 2)  # GB
        
        # 系统信息
        system_info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "ip_address": "127.0.0.1",
            "processor": platform.processor()
        }
        
        return {
            "success": True,
            "data": {
                "cpu": {
                    "percent": cpu_percent
                },
                "memory": {
                    "percent": memory_percent,
                    "used": memory_used,
                    "total": memory_total
                },
                "disk": {
                    "percent": disk_percent,
                    "used": disk_used,
                    "total": disk_total
                },
                "system": system_info,
                "timestamp": datetime.now().isoformat()
            },
            "message": "系统资源获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统资源失败: {str(e)}")