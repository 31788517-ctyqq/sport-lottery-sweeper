"""
中间件模块
定义各种HTTP中间件
"""
import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
import logging
import uuid

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件
    记录每个请求的详细信息
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 记录请求信息
        logger.info(f"Request started: {request.method} {request.url.path} "
                   f"[ID: {request_id}] [Client: {request.client.host}]")
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id
            
            # 记录响应信息
            logger.info(f"Request completed: {request.method} {request.url.path} "
                       f"[Status: {response.status_code}] "
                       f"[Time: {process_time:.3f}s] [ID: {request_id}]")
            
            return response
            
        except Exception as e:
            # 记录异常信息
            process_time = time.time() - start_time
            logger.error(f"Request failed: {request.method} {request.url.path} "
                        f"[Error: {str(e)}] [Time: {process_time:.3f}s] [ID: {request_id}]")
            raise


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    认证中间件
    验证JWT令牌并设置用户上下文
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 检查请求头中的认证令牌
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            request.state.token = token
            
            # 这里可以添加令牌验证逻辑
            # 验证成功后设置用户信息到request.state
            
        return await call_next(request)


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    压缩中间件
    对响应进行GZIP压缩
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 检查是否支持压缩
        accept_encoding = request.headers.get("Accept-Encoding", "")
        
        if "gzip" in accept_encoding and len(response.body) > 1024:
            import gzip
            import io
            
            # 创建压缩响应
            compressed = io.BytesIO()
            with gzip.GzipFile(fileobj=compressed, mode='wb') as f:
                f.write(response.body)
            
            response.body = compressed.getvalue()
            response.headers["Content-Encoding"] = "gzip"
            response.headers["Content-Length"] = str(len(response.body))
        
        return response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """
    缓存控制中间件
    设置HTTP缓存头
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 根据路径设置缓存策略
        path = request.url.path
        
        if path.startswith("/api/"):
            # API响应不缓存
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        elif path.startswith("/static/"):
            # 静态资源缓存
            response.headers["Cache-Control"] = "public, max-age=31536000"
        else:
            # 默认缓存策略
            response.headers["Cache-Control"] = "no-cache"
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    安全头中间件
    添加各种安全相关的HTTP头
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 添加安全头
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), camera=()"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    请求ID中间件
    为每个请求生成唯一ID
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        import uuid
        
        # 生成或获取请求ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class DatabaseSessionMiddleware(BaseHTTPMiddleware):
    """
    数据库会话中间件
    为每个请求提供数据库会话
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        from ..core.database import get_db_session
        
        async with get_db_session() as session:
            request.state.db = session
            response = await call_next(request)
        
        return response


# 中间件配置
def setup_middlewares(app):
    """
    配置所有中间件
    """
    # 注意：中间件的添加顺序很重要！
    
    # 1. 请求ID中间件（最先添加）
    app.add_middleware(RequestIDMiddleware)
    
    # 2. 请求日志中间件
    app.add_middleware(RequestLoggingMiddleware)
    
    # 3. 认证中间件
    app.add_middleware(AuthenticationMiddleware)
    
    # 4. 数据库会话中间件
    app.add_middleware(DatabaseSessionMiddleware)
    
    # 5. 安全头中间件
    app.add_middleware(SecurityHeadersMiddleware)
    
    # 6. 缓存控制中间件
    app.add_middleware(CacheControlMiddleware)
    
    # 7. 压缩中间件（最后添加，因为它修改响应体）
    app.add_middleware(CompressionMiddleware)
    
    logger.info("所有中间件已配置完成")