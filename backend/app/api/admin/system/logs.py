"""
日志管理API端点
提供日志文件监控、轮转管理和清理功能
"""
from fastapi import APIRouter, Depends, HTTPException
from backend.utils.log_manager import log_manager
from typing import Dict, Any

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