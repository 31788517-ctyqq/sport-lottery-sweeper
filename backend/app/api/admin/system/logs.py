"""
日志管理API端点
提供日志文件监控、轮转管理和清理功能
"""
from fastapi import APIRouter, Depends, HTTPException
from backend.utils.log_manager import log_manager
from typing import Dict, Any
from datetime import datetime
from backend.database import get_db
from backend.core.auth import get_current_admin_user
from backend.models.admin_user import AdminUser
from sqlalchemy.orm import Session
from backend.services.log_service import LogService
from backend.schemas.log_entry import LogEntryWithCount

router = APIRouter()

@router.get("/logs/statistics",
           summary="日志统计信息",
           description="获取日志文件的统计信息和存储使用情况")
async def get_log_statistics() -> Dict[str, Any]:
    """
    获取日志统计信息
    """
    try:
        stats = log_manager.get_log_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日志统计失败: {str(e)}")

@router.get("/logs/files",
           summary="日志文件列表",
           description="获取所有日志文件的详细信息")
async def get_log_files() -> Dict[str, Any]:
    """
    获取日志文件列表
    """
    try:
        files = log_manager.get_log_files()
        return {
            "files": files,
            "total_count": len(files),
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日志文件列表失败: {str(e)}")

@router.post("/logs/cleanup",
            summary="清理旧日志",
            description="清理指定天数前的日志文件")
async def cleanup_logs(days: int = None) -> Dict[str, Any]:
    """
    清理旧日志文件
    """
    try:
        result = log_manager.cleanup_old_logs(days)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"清理日志失败: {result.get('error', '未知错误')}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清理日志失败: {str(e)}")

@router.post("/logs/rotate",
            summary="手动轮转日志",
            description="手动触发日志轮转操作")
async def rotate_logs() -> Dict[str, Any]:
    """
    手动触发日志轮转
    """
    try:
        result = log_manager.rotate_logs_manually()
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"日志轮转失败: {result.get('error', '未知错误')}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"日志轮转失败: {str(e)}")

@router.post("/logs/archive",
            summary="归档日志",
            description="将当前日志文件打包归档")
async def archive_logs(archive_name: str = None) -> Dict[str, Any]:
    """
    归档日志文件
    """
    try:
        result = log_manager.archive_logs(archive_name)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"日志归档失败: {result.get('error', '未知错误')}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"日志归档失败: {str(e)}")

@router.get("/logs/config",
           summary="日志配置信息",
           description="获取当前日志系统的配置参数")
async def get_log_config() -> Dict[str, Any]:
    """
    获取日志配置信息
    """
    try:
        config = log_manager.get_current_log_config()
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日志配置失败: {str(e)}")

@router.delete("/logs/file/{filename}",
               summary="删除日志文件",
               description="删除指定的日志文件")
async def delete_log_file(filename: str) -> Dict[str, Any]:
    """
    删除指定的日志文件
    """
    try:
        log_file = log_manager.log_dir / filename
        
        # 安全检查：只允许删除.log文件
        if not filename.endswith('.log'):
            raise HTTPException(status_code=400, detail="只能删除.log文件")
        
        # 安全检查：不允许删除正在使用的日志文件
        protected_files = ['app.log', 'error.log', 'access.log']
        if filename in protected_files:
            raise HTTPException(status_code=400, detail="不能删除正在使用的活跃日志文件")
        
        if not log_file.exists():
            raise HTTPException(status_code=404, detail="日志文件不存在")
        
        file_size = log_file.stat().st_size
        log_file.unlink()
        
        return {
            "success": True,
            "deleted_file": filename,
            "file_size": file_size,
            "file_size_mb": round(file_size / 1024 / 1024, 2),
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除日志文件失败: {str(e)}")


# ==================== 新增：数据库日志相关API ====================

@router.get("/logs/db/system",
           summary="获取系统日志",
           description="从数据库获取系统日志信息")
async def get_system_logs(
    skip: int = 0,
    limit: int = 20,
    level: str = None,
    module: str = None,
    start_date: str = None,
    end_date: str = None,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    获取系统日志
    """
    try:
        # 解析日期参数
        from datetime import datetime
        parsed_start_date = datetime.fromisoformat(start_date) if start_date else None
        parsed_end_date = datetime.fromisoformat(end_date) if end_date else None
        
        log_service = LogService(db)
        logs, total = log_service.get_log_entries(
            skip=skip,
            limit=limit,
            level=level,
            module=module,
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            search=search
        )
        
        return {
            "items": logs,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统日志失败: {str(e)}")


@router.get("/logs/db/user",
           summary="获取用户日志",
           description="从数据库获取用户活动日志信息")
async def get_user_logs(
    skip: int = 0,
    limit: int = 20,
    user_id: int = None,
    level: str = None,
    start_date: str = None,
    end_date: str = None,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    获取用户日志
    """
    try:
        # 解析日期参数
        from datetime import datetime
        parsed_start_date = datetime.fromisoformat(start_date) if start_date else None
        parsed_end_date = datetime.fromisoformat(end_date) if end_date else None
        
        log_service = LogService(db)
        logs, total = log_service.get_log_entries(
            skip=skip,
            limit=limit,
            user_id=user_id,
            level=level,
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            search=search
        )
        
        return {
            "items": logs,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户日志失败: {str(e)}")


@router.get("/logs/db/security",
           summary="获取安全日志",
           description="从数据库获取安全相关日志信息")
async def get_security_logs(
    skip: int = 0,
    limit: int = 20,
    level: str = None,
    start_date: str = None,
    end_date: str = None,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    获取安全日志
    """
    try:
        # 解析日期参数
        from datetime import datetime
        parsed_start_date = datetime.fromisoformat(start_date) if start_date else None
        parsed_end_date = datetime.fromisoformat(end_date) if end_date else None
        
        log_service = LogService(db)
        logs, total = log_service.get_log_entries(
            skip=skip,
            limit=limit,
            level=level,
            module="security",  # 特定的安全模块
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            search=search
        )
        
        return {
            "items": logs,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取安全日志失败: {str(e)}")


@router.get("/logs/db/api",
           summary="获取API日志",
           description="从数据库获取API访问日志信息")
async def get_api_logs(
    skip: int = 0,
    limit: int = 20,
    level: str = None,
    start_date: str = None,
    end_date: str = None,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    获取API日志
    """
    try:
        # 解析日期参数
        from datetime import datetime
        parsed_start_date = datetime.fromisoformat(start_date) if start_date else None
        parsed_end_date = datetime.fromisoformat(end_date) if end_date else None
        
        log_service = LogService(db)
        logs, total = log_service.get_log_entries(
            skip=skip,
            limit=limit,
            level=level,
            module="api",  # 特定的API模块
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            search=search
        )
        
        return {
            "items": logs,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取API日志失败: {str(e)}")


@router.get("/logs/db/statistics",
           summary="获取数据库日志统计",
           description="从数据库获取日志统计信息")
async def get_log_statistics_from_db(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    获取数据库日志统计
    """
    try:
        log_service = LogService(db)
        stats = log_service.get_log_statistics()
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日志统计失败: {str(e)}")