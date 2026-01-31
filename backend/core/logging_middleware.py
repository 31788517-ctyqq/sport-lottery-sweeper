"""
日志中间件
自动记录系统日志、用户日志、安全日志和API访问日志
"""
# AI_WORKING: coder1 @2026-01-29 - 统一使用Python logging模块，移除print语句
import time
import uuid
import logging
from datetime import datetime
from typing import Callable, Any
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.log_entry import LogEntry

logger = logging.getLogger(__name__)
# AI_DONE: coder1 @2026-01-29


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        # 记录请求开始时间
        start_time = time.time()
        
        # 生成请求ID
        request_id = str(uuid.uuid4())
        
        # 存储请求ID到请求状态中
        request.state.request_id = request_id
        
        # 获取客户端IP
        client_ip = self.get_client_ip(request)
        
        # 获取用户ID（如果存在）
        user_id = self.get_user_id(request)
        
        # 记录请求日志
        self.log_request(request, client_ip, user_id)
        
        # 处理请求
        try:
            response = await call_next(request)
        except Exception as e:
            # 记录错误日志
            self.log_error(request, e, client_ip, user_id)
            raise
        
        # 计算请求耗时
        duration = time.time() - start_time
        
        # 记录响应日志
        self.log_response(request, response, duration, client_ip, user_id)
        
        # 设置响应头
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(duration)
        
        return response
    
    def get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host
    
    def get_user_id(self, request: Request) -> int:
        """获取用户ID"""
        # 从JWT token或其他认证方式中提取用户ID
        # 这里只是一个示例，实际实现取决于你的认证系统
        try:
            # 如果用户已认证，可以从JWT token中提取用户ID
            # 例如: request.state.current_user.id
            if hasattr(request.state, 'current_user') and request.state.current_user:
                return getattr(request.state.current_user, 'id', None)
            return None
        except:
            return None
    
    def log_request(self, request: Request, client_ip: str, user_id: int = None) -> None:
        """记录请求日志"""
        try:
            # 为每个请求创建一个新的数据库会话
            db = next(get_db())
            
            log_entry = LogEntry(
                timestamp=datetime.utcnow(),
                level="INFO",
                module="api",
                message=f"{request.method} {request.url.path}",
                user_id=user_id,
                ip_address=client_ip,
                user_agent=request.headers.get("User-Agent"),
                session_id=None,
                request_path=str(request.url.path),
                response_status=None,
                duration_ms=None,
                extra_data=f"method={request.method}, path={request.url.path}"
            )
            
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
            db.close()
        except Exception as e:
            logger.error(f"Failed to log request: {str(e)}")
    
    def log_response(self, request: Request, response, duration: float, client_ip: str, user_id: int = None) -> None:
        """记录响应日志"""
        try:
            db = next(get_db())
            
            log_entry = LogEntry(
                timestamp=datetime.utcnow(),
                level="INFO" if response.status_code < 400 else "WARN",
                module="api",
                message=f"Response {response.status_code}",
                user_id=user_id,
                ip_address=client_ip,
                user_agent=request.headers.get("User-Agent"),
                session_id=None,
                request_path=str(request.url.path),
                response_status=response.status_code,
                duration_ms=int(duration * 1000),
                extra_data=f"method={request.method}, path={request.url.path}, duration={duration:.3f}s"
            )
            
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
            db.close()
        except Exception as e:
            logger.error(f"Failed to log response: {str(e)}")
    
    def log_error(self, request: Request, error: Exception, client_ip: str, user_id: int = None) -> None:
        """记录错误日志"""
        try:
            db = next(get_db())
            
            log_entry = LogEntry(
                timestamp=datetime.utcnow(),
                level="ERROR",
                module="api",
                message=f"Error: {str(error)}",
                user_id=user_id,
                ip_address=client_ip,
                user_agent=request.headers.get("User-Agent"),
                session_id=None,
                request_path=str(request.url.path),
                response_status=500,
                duration_ms=None,
                extra_data=f"method={request.method}, path={request.url.path}, error_type={type(error).__name__}"
            )
            
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
            db.close()
        except Exception as e:
            logger.error(f"Failed to log error: {str(e)}")
    
    def log_security_event(self, event_type: str, user_id: int, ip_address: str, details: str = "") -> None:
        """记录安全事件日志"""
        try:
            db = next(get_db())
            
            log_entry = LogEntry(
                timestamp=datetime.utcnow(),
                level="INFO" if event_type.lower() in ['login', 'logout'] else "WARN",
                module="security",
                message=f"Security event: {event_type} - {details}",
                user_id=user_id,
                ip_address=ip_address,
                user_agent=None,
                session_id=None,
                request_path=None,
                response_status=None,
                duration_ms=None,
                extra_data=details
            )
            
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
            db.close()
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")