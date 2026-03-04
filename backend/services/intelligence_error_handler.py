"""
情报系统错误处理器
提供统一的异常处理、日志记录和错误响应机制
"""
import logging
import traceback
import sys
from datetime import datetime
from typing import Optional, Dict, Any, Type, Callable, Union
from functools import wraps
from enum import Enum
import json
from dataclasses import dataclass, asdict

from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from pydantic import ValidationError


class ErrorSeverity(Enum):
    """错误严重程度枚举"""
    DEBUG = "debug"        # 调试信息
    INFO = "info"          # 普通信息
    WARNING = "warning"    # 警告
    ERROR = "error"        # 错误
    CRITICAL = "critical"  # 严重错误


class ErrorCategory(Enum):
    """错误分类枚举"""
    DATABASE = "database"              # 数据库错误
    VALIDATION = "validation"          # 数据验证错误
    NETWORK = "network"                # 网络错误
    AUTHENTICATION = "authentication"  # 认证错误
    AUTHORIZATION = "authorization"    # 授权错误
    BUSINESS_LOGIC = "business_logic" # 业务逻辑错误
    SYSTEM = "system"                  # 系统错误
    EXTERNAL_SERVICE = "external_service"  # 外部服务错误
    UNKNOWN = "unknown"                # 未知错误


@dataclass
class ErrorContext:
    """错误上下文信息"""
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    http_method: Optional[str] = None
    request_params: Optional[Dict[str, Any]] = None
    request_body: Optional[Dict[str, Any]] = None
    response_status: Optional[int] = None
    execution_time_ms: Optional[float] = None


@dataclass
class ErrorInfo:
    """错误信息"""
    error_id: str
    timestamp: str
    message: str
    exception_type: str
    exception_details: Optional[str] = None
    stack_trace: Optional[str] = None
    severity: ErrorSeverity = ErrorSeverity.ERROR
    category: ErrorCategory = ErrorCategory.UNKNOWN
    context: Optional[ErrorContext] = None
    metadata: Optional[Dict[str, Any]] = None


class IntelligenceError(Exception):
    """情报系统基础异常类"""
    
    def __init__(self, 
                 message: str,
                 severity: ErrorSeverity = ErrorSeverity.ERROR,
                 category: ErrorCategory = ErrorCategory.BUSINESS_LOGIC,
                 context: Optional[ErrorContext] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        初始化异常
        
        Args:
            message: 错误消息
            severity: 严重程度
            category: 错误分类
            context: 错误上下文
            metadata: 附加元数据
        """
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.category = category
        self.context = context
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()
        self.error_id = self._generate_error_id()
    
    def _generate_error_id(self) -> str:
        """生成错误ID"""
        import uuid
        return f"INTEL_ERR_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "error_id": self.error_id,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "timestamp": self.timestamp,
            "context": asdict(self.context) if self.context else None,
            "metadata": self.metadata
        }


class IntelligenceErrorHandler:
    """
    情报系统错误处理器
    提供统一的异常捕获、日志记录和错误响应
    """
    
    def __init__(self, 
                 logger: Optional[logging.Logger] = None,
                 enable_error_tracking: bool = True,
                 log_stack_trace: bool = True):
        """
        初始化错误处理器
        
        Args:
            logger: 日志记录器，如果为None则创建新的
            enable_error_tracking: 是否启用错误跟踪
            log_stack_trace: 是否记录堆栈跟踪
        """
        self.logger = logger or logging.getLogger(__name__)
        self.enable_error_tracking = enable_error_tracking
        self.log_stack_trace = log_stack_trace
        self._error_stats = {
            "total_errors": 0,
            "by_category": {cat.value: 0 for cat in ErrorCategory},
            "by_severity": {sev.value: 0 for sev in ErrorSeverity},
            "recent_errors": []
        }
    
    def handle_exception(self, 
                        exception: Exception,
                        context: Optional[ErrorContext] = None,
                        log_level: Optional[ErrorSeverity] = None) -> ErrorInfo:
        """
        处理异常
        
        Args:
            exception: 异常对象
            context: 错误上下文
            log_level: 日志级别，如果为None则根据异常类型自动确定
            
        Returns:
            ErrorInfo: 错误信息
        """
        # 生成错误信息
        error_info = self._create_error_info(exception, context)
        
        # 自动确定日志级别
        if log_level is None:
            log_level = self._determine_log_level(exception)
        
        # 记录错误
        self._log_error(error_info, log_level)
        
        # 更新统计信息
        self._update_error_stats(error_info)
        
        # 错误跟踪（如需要）
        if self.enable_error_tracking:
            self._track_error(error_info)
        
        return error_info
    
    def wrap_function(self, 
                     func: Callable,
                     default_return: Optional[Any] = None,
                     log_errors: bool = True) -> Callable:
        """
        包装函数，自动捕获和处理异常
        
        Args:
            func: 要包装的函数
            default_return: 发生错误时的默认返回值
            log_errors: 是否记录错误
            
        Returns:
            Callable: 包装后的函数
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    error_info = self.handle_exception(e)
                    
                    # 记录函数调用信息
                    if error_info.context is None:
                        error_info.context = ErrorContext()
                    
                    error_info.metadata.update({
                        "function_name": func.__name__,
                        "module_name": func.__module__,
                        "args": str(args)[:200],  # 限制长度
                        "kwargs": str(kwargs)[:200]
                    })
                
                # 返回默认值
                if default_return is not None:
                    return default_return
                
                # 重新抛出原始异常
                raise
        
        return wrapper
    
    def wrap_api_endpoint(self, 
                         endpoint_func: Callable,
                         include_request_info: bool = True) -> Callable:
        """
        包装API端点，自动捕获和处理异常
        
        Args:
            endpoint_func: API端点函数
            include_request_info: 是否包含请求信息
            
        Returns:
            Callable: 包装后的端点函数
        """
        @wraps(endpoint_func)
        async def wrapper(*args, **kwargs):
            try:
                return await endpoint_func(*args, **kwargs)
            except Exception as e:
                context = None
                
                # 提取请求信息（如果可用）
                if include_request_info:
                    context = self._extract_request_context(endpoint_func, *args, **kwargs)
                
                error_info = self.handle_exception(e, context)
                
                # 转换为HTTP响应
                return self._create_error_response(error_info)
        
        return wrapper
    
    def get_error_stats(self) -> Dict[str, Any]:
        """
        获取错误统计信息
        
        Returns:
            Dict[str, Any]: 错误统计
        """
        return {
            "total_errors": self._error_stats["total_errors"],
            "by_category": self._error_stats["by_category"],
            "by_severity": self._error_stats["by_severity"],
            "recent_error_count": len(self._error_stats["recent_errors"])
        }
    
    def clear_error_stats(self) -> None:
        """清除错误统计"""
        self._error_stats = {
            "total_errors": 0,
            "by_category": {cat.value: 0 for cat in ErrorCategory},
            "by_severity": {sev.value: 0 for sev in ErrorSeverity},
            "recent_errors": []
        }
    
    def log_system_event(self, 
                        message: str,
                        severity: ErrorSeverity = ErrorSeverity.INFO,
                        metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        记录系统事件
        
        Args:
            message: 事件消息
            severity: 严重程度
            metadata: 附加元数据
        """
        event_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "system_event",
            "message": message,
            "severity": severity.value,
            "metadata": metadata or {}
        }
        
        log_method = getattr(self.logger, severity.value.lower())
        log_method(f"系统事件: {message}", extra={"event_data": json.dumps(event_data)})
    
    def log_operation(self, 
                     operation: str,
                     status: str,
                     duration_ms: float,
                     metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        记录操作日志
        
        Args:
            operation: 操作名称
            status: 操作状态（success, failed, warning）
            duration_ms: 执行时间（毫秒）
            metadata: 附加元数据
        """
        operation_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "status": status,
            "duration_ms": round(duration_ms, 2),
            "metadata": metadata or {}
        }
        
        log_level = logging.INFO
        if status == "failed":
            log_level = logging.ERROR
        elif status == "warning":
            log_level = logging.WARNING
        
        self.logger.log(log_level, f"操作日志: {operation} - {status}", 
                       extra={"operation_data": json.dumps(operation_data)})
    
    def _create_error_info(self, 
                          exception: Exception,
                          context: Optional[ErrorContext]) -> ErrorInfo:
        """创建错误信息"""
        error_id = self._generate_error_id()
        
        # 提取异常信息
        exception_type = type(exception).__name__
        exception_details = str(exception)
        
        # 提取堆栈跟踪
        stack_trace = None
        if self.log_stack_trace:
            stack_trace = self._format_stack_trace(exception)
        
        # 确定错误分类和严重程度
        category = self._determine_error_category(exception)
        severity = self._determine_error_severity(exception)
        
        return ErrorInfo(
            error_id=error_id,
            timestamp=datetime.utcnow().isoformat(),
            message=exception_details,
            exception_type=exception_type,
            exception_details=exception_details,
            stack_trace=stack_trace,
            severity=severity,
            category=category,
            context=context
        )
    
    def _determine_error_category(self, exception: Exception) -> ErrorCategory:
        """根据异常类型确定错误分类"""
        if isinstance(exception, (SQLAlchemyError,)):
            return ErrorCategory.DATABASE
        elif isinstance(exception, (ValidationError,)):
            return ErrorCategory.VALIDATION
        elif isinstance(exception, (ConnectionError, TimeoutError)):
            return ErrorCategory.NETWORK
        elif isinstance(exception, (HTTPException,)) and exception.status_code in [401, 403]:
            return ErrorCategory.AUTHENTICATION if exception.status_code == 401 else ErrorCategory.AUTHORIZATION
        elif isinstance(exception, (IntelligenceError,)):
            return exception.category
        elif isinstance(exception, (ValueError, TypeError, AttributeError)):
            return ErrorCategory.BUSINESS_LOGIC
        else:
            return ErrorCategory.UNKNOWN
    
    def _determine_error_severity(self, exception: Exception) -> ErrorSeverity:
        """根据异常类型确定严重程度"""
        if isinstance(exception, (KeyboardInterrupt, SystemExit)):
            return ErrorSeverity.CRITICAL
        elif isinstance(exception, (MemoryError, OSError)):
            return ErrorSeverity.CRITICAL
        elif isinstance(exception, (SQLAlchemyError,)):
            return ErrorSeverity.ERROR
        elif isinstance(exception, (HTTPException,)) and exception.status_code >= 500:
            return ErrorSeverity.ERROR
        elif isinstance(exception, (IntelligenceError,)):
            return exception.severity
        else:
            return ErrorSeverity.WARNING
    
    def _determine_log_level(self, exception: Exception) -> ErrorSeverity:
        """根据异常确定日志级别"""
        severity = self._determine_error_severity(exception)
        
        # 将严重程度映射到日志级别
        log_level_map = {
            ErrorSeverity.DEBUG: ErrorSeverity.DEBUG,
            ErrorSeverity.INFO: ErrorSeverity.INFO,
            ErrorSeverity.WARNING: ErrorSeverity.WARNING,
            ErrorSeverity.ERROR: ErrorSeverity.ERROR,
            ErrorSeverity.CRITICAL: ErrorSeverity.CRITICAL
        }
        
        return log_level_map.get(severity, ErrorSeverity.ERROR)
    
    def _log_error(self, error_info: ErrorInfo, log_level: ErrorSeverity) -> None:
        """记录错误"""
        log_message = f"[{error_info.error_id}] {error_info.message}"
        
        # 添加额外信息
        extra_info = {
            "error_id": error_info.error_id,
            "exception_type": error_info.exception_type,
            "category": error_info.category.value,
            "timestamp": error_info.timestamp,
            "context": asdict(error_info.context) if error_info.context else None
        }
        
        # 如果有堆栈跟踪，添加到日志消息
        if error_info.stack_trace and self.log_stack_trace:
            log_message += f"\n{error_info.stack_trace}"
        
        # 记录日志
        log_method = getattr(self.logger, log_level.value.lower())
        log_method(log_message, extra={"error_info": json.dumps(asdict(error_info))})
    
    def _update_error_stats(self, error_info: ErrorInfo) -> None:
        """更新错误统计"""
        self._error_stats["total_errors"] += 1
        self._error_stats["by_category"][error_info.category.value] += 1
        self._error_stats["by_severity"][error_info.severity.value] += 1
        
        # 保持最近错误记录
        self._error_stats["recent_errors"].append(error_info)
        if len(self._error_stats["recent_errors"]) > 100:
            self._error_stats["recent_errors"] = self._error_stats["recent_errors"][-100:]
    
    def _track_error(self, error_info: ErrorInfo) -> None:
        """跟踪错误（可根据需要扩展）"""
        # 这里可以添加错误跟踪逻辑，如发送到错误监控服务
        pass
    
    def _generate_error_id(self) -> str:
        """生成错误ID"""
        import uuid
        return f"INTEL_ERR_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    def _format_stack_trace(self, exception: Exception) -> str:
        """格式化堆栈跟踪"""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_traceback:
            stack_trace_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            return "\n".join(stack_trace_lines)
        return ""
    
    def _extract_request_context(self, 
                                endpoint_func: Callable,
                                *args, **kwargs) -> Optional[ErrorContext]:
        """
        提取请求上下文信息
        
        Note: 这个方法是框架特定的，需要根据实际使用的Web框架进行调整
        """
        context = ErrorContext()
        
        try:
            # 尝试从FastAPI请求对象提取信息
            # 注意：这里假设端点是FastAPI路由处理器
            for arg in args:
                if hasattr(arg, '__class__') and 'Request' in str(arg.__class__):
                    request = arg
                    
                    # 提取基本信息
                    context.endpoint = request.url.path
                    context.http_method = request.method
                    
                    # 尝试提取用户ID（根据实际认证实现）
                    if hasattr(request.state, 'user_id'):
                        context.user_id = request.state.user_id
                    
                    # 提取查询参数
                    if request.query_params:
                        context.request_params = dict(request.query_params)
                    
                    # 提取请求体（注意：可能不是所有请求都有体）
                    if hasattr(request, 'body'):
                        try:
                            body = await request.body()
                            if body:
                                context.request_body = json.loads(body)
                        except:
                            pass
                    
                    break
            
            # 尝试从额外信息提取
            for key, value in kwargs.items():
                if key.lower() == 'user_id':
                    context.user_id = value
                elif key.lower() == 'session_id':
                    context.session_id = value
                elif key.lower() == 'request_id':
                    context.request_id = value
        
        except Exception as e:
            self.logger.warning(f"提取请求上下文失败: {str(e)}")
        
        return context
    
    def _create_error_response(self, error_info: ErrorInfo) -> Dict[str, Any]:
        """创建错误响应"""
        return {
            "success": False,
            "error": {
                "id": error_info.error_id,
                "code": error_info.category.value.upper(),
                "message": error_info.message,
                "timestamp": error_info.timestamp,
                "details": error_info.exception_details
            },
            "timestamp": datetime.utcnow().isoformat()
        }


# 预定义的错误类型
class DatabaseError(IntelligenceError):
    """数据库错误"""
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(message, ErrorSeverity.ERROR, ErrorCategory.DATABASE, context)


class ValidationError(IntelligenceError):
    """验证错误"""
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(message, ErrorSeverity.WARNING, ErrorCategory.VALIDATION, context)


class AuthenticationError(IntelligenceError):
    """认证错误"""
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(message, ErrorSeverity.ERROR, ErrorCategory.AUTHENTICATION, context)


class AuthorizationError(IntelligenceError):
    """授权错误"""
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(message, ErrorSeverity.ERROR, ErrorCategory.AUTHORIZATION, context)


class ExternalServiceError(IntelligenceError):
    """外部服务错误"""
    def __init__(self, message: str, service_name: str, context: Optional[ErrorContext] = None):
        metadata = {"service_name": service_name}
        super().__init__(message, ErrorSeverity.ERROR, ErrorCategory.EXTERNAL_SERVICE, context, metadata)


class DataQualityError(IntelligenceError):
    """数据质量错误"""
    def __init__(self, message: str, quality_score: float, context: Optional[ErrorContext] = None):
        metadata = {"quality_score": quality_score}
        super().__init__(message, ErrorSeverity.WARNING, ErrorCategory.BUSINESS_LOGIC, context, metadata)


# 全局错误处理器实例
global_error_handler = IntelligenceErrorHandler()


# 装饰器函数
def handle_errors(default_return: Optional[Any] = None, log_errors: bool = True):
    """
    错误处理装饰器
    
    Args:
        default_return: 发生错误时的默认返回值
        log_errors: 是否记录错误
    
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    global_error_handler.handle_exception(e)
                
                if default_return is not None:
                    return default_return
                
                raise
        
        return wrapper
    
    return decorator


# 日志配置示例函数
def configure_intelligence_logging(
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    enable_console: bool = True,
    enable_file: bool = True,
    max_file_size_mb: int = 10,
    backup_count: int = 5) -> logging.Logger:
    """
    配置情报系统日志
    
    Args:
        log_file: 日志文件路径，如果为None则使用默认路径
        log_level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        enable_console: 是否启用控制台日志
        enable_file: 是否启用文件日志
        max_file_size_mb: 单个日志文件最大大小（MB）
        backup_count: 保留的备份文件数量
    
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    import os
    from logging.handlers import RotatingFileHandler
    
    # 创建日志记录器
    logger = logging.getLogger("intelligence")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n'
        'Context: %(error_info)s' if '%(error_info)s' in formatter._fmt else ''
    )
    
    # 控制台处理器
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 文件处理器
    if enable_file and log_file:
        # 确保日志目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_file_size_mb * 1024 * 1024,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # 添加自定义过滤器以处理额外字段
    class ContextFilter(logging.Filter):
        def filter(self, record):
            if not hasattr(record, 'error_info'):
                record.error_info = '{}'
            return True
    
    logger.addFilter(ContextFilter())
    
    return logger


# 使用示例
if __name__ == "__main__":
    # 配置日志
    logger = configure_intelligence_logging(
        log_file="logs/intelligence_errors.log",
        log_level="DEBUG",
        enable_console=True,
        enable_file=True
    )
    
    # 创建错误处理器
    error_handler = IntelligenceErrorHandler(logger=logger)
    
    # 示例函数
    @error_handler.wrap_function(default_return=None)
    def example_function(value: int) -> int:
        if value < 0:
            raise ValueError("值不能为负数")
        return value * 2
    
    # 测试错误处理
    print("测试错误处理:")
    print("1. 正常情况:", example_function(5))
    print("2. 错误情况:", example_function(-5))
    
    # 获取统计信息
    stats = error_handler.get_error_stats()
    print("\n错误统计:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))