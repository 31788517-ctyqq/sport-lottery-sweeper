"""
日志管理工具
提供日志轮转策略的动态管理和监控功能
"""
import logging
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
from backend.config import settings
from backend.utils.logging_config import DEFAULT_LOG_CONFIG

class LogManager:
    """日志管理器"""
    
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
    
    def get_log_files(self) -> List[Dict[str, Any]]:
        """获取所有日志文件信息"""
        log_files = []
        
        if not self.log_dir.exists():
            return log_files
        
        for log_file in self.log_dir.iterdir():
            if log_file.is_file() and log_file.suffix == '.log':
                stat = log_file.stat()
                log_files.append({
                    "name": log_file.name,
                    "path": str(log_file),
                    "size": stat.st_size,
                    "size_mb": round(stat.st_size / 1024 / 1024, 2),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
        
        return sorted(log_files, key=lambda x: x["modified"], reverse=True)
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """获取日志统计信息"""
        log_files = self.get_log_files()
        total_size = sum(f["size"] for f in log_files)
        
        # 按类型分组
        log_types = {
            "application": [f for f in log_files if f["name"] == "app.log" or f["name"].startswith("app.log.")],
            "error": [f for f in log_files if f["name"] == "error.log" or f["name"].startswith("error.log.")],
            "access": [f for f in log_files if f["name"] == "access.log" or f["name"].startswith("access.log.")],
            "other": [f for f in log_files if f["name"] not in ["app.log", "error.log", "access.log"] and not any(f["name"].startswith(prefix) for prefix in ["app.log.", "error.log.", "access.log."])]
        }
        
        type_stats = {}
        for log_type, files in log_types.items():
            type_total_size = sum(f["size"] for f in files)
            type_stats[log_type] = {
                "file_count": len(files),
                "total_size": type_total_size,
                "total_size_mb": round(type_total_size / 1024 / 1024, 2)
            }
        
        return {
            "total_files": len(log_files),
            "total_size": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "by_type": type_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def cleanup_old_logs(self, days: int = None) -> Dict[str, Any]:
        """清理指定天数前的日志文件"""
        if days is None:
            days = settings.LOG_BACKUP_COUNT
        
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_files = []
        total_size_freed = 0
        
        try:
            for log_file in self.log_dir.iterdir():
                if log_file.is_file() and log_file.suffix == '.log':
                    file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        file_size = log_file.stat().st_size
                        log_file.unlink()
                        cleaned_files.append({
                            "name": log_file.name,
                            "size": file_size,
                            "size_mb": round(file_size / 1024 / 1024, 2)
                        })
                        total_size_freed += file_size
            
            return {
                "cleaned_files": cleaned_files,
                "total_files_cleaned": len(cleaned_files),
                "total_size_freed": total_size_freed,
                "total_size_freed_mb": round(total_size_freed / 1024 / 1024, 2),
                "cutoff_date": cutoff_date.isoformat(),
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "cleaned_files": cleaned_files,
                "total_files_cleaned": len(cleaned_files)
            }
    
    def rotate_logs_manually(self) -> Dict[str, Any]:
        """手动触发日志轮转"""
        try:
            # 重新设置日志配置以触发轮转
            from backend.utils import logging_config
            
            # 获取当前日志器
            root_logger = logging.getLogger()
            
            # 临时移除文件处理器
            file_handlers = [h for h in root_logger.handlers if isinstance(h, logging.FileHandler)]
            for handler in file_handlers:
                handler.close()
                root_logger.removeHandler(handler)
            
            # 重新设置日志
            logging_config.setup_logging()
            
            return {
                "success": True,
                "message": "日志轮转完成",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def archive_logs(self, archive_name: str = None) -> Dict[str, Any]:
        """归档当前日志文件"""
        if archive_name is None:
            archive_name = f"logs_archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        try:
            import zipfile
            
            archive_path = self.log_dir / archive_name
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for log_file in self.log_dir.iterdir():
                    if log_file.is_file() and log_file.suffix == '.log' and not log_file.name.startswith('logs_archive'):
                        zipf.write(log_file, log_file.name)
            
            archive_size = archive_path.stat().st_size
            
            return {
                "success": True,
                "archive_path": str(archive_path),
                "archive_size": archive_size,
                "archive_size_mb": round(archive_size / 1024 / 1024, 2),
                "files_archived": len(list(self.log_dir.glob("*.log"))),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_current_log_config(self) -> Dict[str, Any]:
        """获取当前日志配置"""
        return {
            "log_level": settings.LOG_LEVEL,
            "log_file_max_bytes": settings.LOG_FILE_MAX_BYTES,
            "log_backup_count": settings.LOG_BACKUP_COUNT,
            "log_rotation_interval": settings.LOG_ROTATION_INTERVAL,
            "log_encoding": settings.LOG_ENCODING,
            "log_cleanup_enabled": settings.LOG_CLEANUP_ENABLED,
            "log_error_backup_multiplier": settings.LOG_ERROR_BACKUP_MULTIPLIER,
            "log_access_rotation": settings.LOG_ACCESS_ROTATION,
            "log_access_backup_count": settings.LOG_ACCESS_BACKUP_COUNT,
            "default_config": DEFAULT_LOG_CONFIG,
            "timestamp": datetime.now().isoformat()
        }

# 全局日志管理器实例
log_manager = LogManager()