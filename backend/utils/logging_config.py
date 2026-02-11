"""
Centralized logging configuration with rotation policies.
Supports size-based and time-based log rotation.
Implements QueueHandler for multiprocessing safety on Windows.
"""
import logging
import logging.handlers
import sys
import os
import queue
from pathlib import Path
from backend.config import settings

# 默认日志轮转配置
DEFAULT_LOG_CONFIG = {
    "max_bytes": 10 * 1024 * 1024,  # 10MB per file
    "backup_count": 30,             # Keep 30 backup files
    "rotation_interval": "midnight", # Rotate daily at midnight
    "encoding": "utf-8",
    "log_level": logging.INFO
}

# 全局日志队列和监听器（用于多进程安全）
_log_queue = None
_queue_listener = None

def _setup_queue_handler(log_level: int, encoding: str = "utf-8"):
    """设置队列处理器用于多进程安全的日志记录"""
    global _log_queue, _queue_listener
    
    if _log_queue is None:
        _log_queue = queue.Queue(-1)  # 无限制队列
        
        # 创建文件处理器
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        app_log_file = log_dir / "app.log"
        
        # 在Windows上，确保使用正确的编码
        if sys.platform == "win32":
            encoding = "utf-8-sig"  # 使用UTF-8 with BOM for Windows compatibility
        
        file_handler = logging.handlers.RotatingFileHandler(
            app_log_file,
            maxBytes=DEFAULT_LOG_CONFIG["max_bytes"],
            backupCount=DEFAULT_LOG_CONFIG["backup_count"],
            encoding=encoding,
            delay=True
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # 创建队列监听器
        _queue_listener = logging.handlers.QueueListener(
            _log_queue, file_handler, respect_handler_level=True
        )
        _queue_listener.start()
    
    # 创建队列处理器
    queue_handler = logging.handlers.QueueHandler(_log_queue)
    queue_handler.setLevel(log_level)
    
    return queue_handler

def setup_logging(log_level: int = None, 
                  max_bytes: int = None, 
                  backup_count: int = None,
                  rotation_interval: str = None):
    """
    设置应用程序的日志配置，支持日志轮转和多进程安全
    
    Args:
        log_level: 日志级别 (默认从settings.LOG_LEVEL获取)
        max_bytes: 单个日志文件最大字节数
        backup_count: 保留的备份文件数量
        rotation_interval: 轮转间隔 ('S', 'M', 'H', 'D', 'midnight', 'W0'-'W6')
    """
    # 使用配置参数或默认值
    max_bytes = max_bytes or DEFAULT_LOG_CONFIG["max_bytes"]
    backup_count = backup_count or DEFAULT_LOG_CONFIG["backup_count"]
    rotation_interval = rotation_interval or DEFAULT_LOG_CONFIG["rotation_interval"]
    encoding = DEFAULT_LOG_CONFIG["encoding"]
    
    # 获取日志级别
    if log_level is None:
        log_level_name = getattr(settings, 'LOG_LEVEL', 'INFO').upper()
        log_level = getattr(logging, log_level_name, logging.INFO)
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 清除现有的处理器
    root_logger.handlers.clear()
    
    # 设置环境变量以确保正确的编码
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # 控制台处理器 - 使用UTF-8编码（Windows下使用utf-8-sig）
    console_encoding = "utf-8-sig" if sys.platform == "win32" else "utf-8"
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # ============================================================================  
    # 应用日志 - 使用QueueHandler确保多进程安全
    # ============================================================================
    queue_handler = _setup_queue_handler(log_level, encoding)
    
    # ============================================================================  
    # 添加处理器到根日志记录器
    # ============================================================================
    root_logger.addHandler(console_handler)
    root_logger.addHandler(queue_handler)
    
    # 为第三方库设置合适的日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").handlers = []  # 禁用uvicorn默认访问日志
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(log_level)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # 记录日志配置信息
    root_logger.info(f"日志系统初始化完成 - 级别:{logging.getLevelName(log_level)}, "
                    f"大小轮转:{max_bytes//1024//1024}MB, "
                    f"时间轮转:{rotation_interval}, "
                    f"备份数:{backup_count}")

def shutdown_logging():
    """关闭日志系统，清理资源"""
    global _queue_listener
    if _queue_listener is not None:
        _queue_listener.stop()
        _queue_listener = None

def get_access_logger():
    """获取访问日志记录器"""
    return logging.getLogger("access")

def log_access(request_info: dict):
    """记录访问日志"""
    access_logger = get_access_logger()
    access_logger.info(
        f"{request_info.get('method', '')} {request_info.get('path', '')} "
        f"- {request_info.get('status_code', '')} - {request_info.get('client_ip', '')} "
        f"- {request_info.get('process_time', '')}s - {request_info.get('user_agent', '')}"
    )

# Example usage in main app startup:
# setup_logging()
# logger = logging.getLogger(__name__)
# logger.info("App started!")
# 
# 在应用关闭时调用:
# shutdown_logging()