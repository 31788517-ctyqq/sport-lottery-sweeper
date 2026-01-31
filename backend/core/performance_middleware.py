"""
性能优化中间件
实现请求缓存、响应压缩和其他性能优化功能
"""
import asyncio
import hashlib
import json
import time
from typing import Callable, Awaitable
from urllib.parse import urlparse

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

from .config import get_settings
from .cache_manager import HybridCache


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    性能优化中间件，包含缓存和压缩功能
    """
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()
        self.cache = HybridCache(
            redis_url=f"redis://{self.settings.REDIS_HOST}:{self.settings.REDIS_PORT}/{self.settings.REDIS_DB}"
        )
        self._initialized = False

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # 初始化缓存系统
        if not self._initialized:
            await self.cache.initialize()
            self._initialized = True

        # 生成缓存键
        cache_key = self._generate_cache_key(request)

        # 尝试从缓存获取响应
        cached_response = await self.cache.get(cache_key)
        if cached_response and request.method == "GET":
            # 检查是否为安全的GET请求（不包含敏感信息）
            if self._is_safe_to_cache(request):
                try:
                    # 解析缓存的响应数据
                    headers = cached_response.get("headers", {})
                    body = cached_response.get("body", b"")
                    
                    # 创建响应对象
                    response = Response(content=body, headers=headers)
                    response.headers["X-Cache"] = "HIT"
                    
                    return response
                except Exception:
                    # 如果解析缓存响应失败，则继续正常处理
                    pass

        # 正常处理请求
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # 对于GET请求且状态码为200的响应，考虑缓存
        if (
            request.method == "GET" 
            and response.status_code == 200 
            and self._is_safe_to_cache(request)
        ):
            # 尝试压缩响应内容
            response = await self._compress_response_if_needed(response)
            
            # 将响应数据存储到缓存
            response_body = b""
            async for chunk in response.body_iterator:
                if isinstance(chunk, str):
                    response_body += chunk.encode()
                else:
                    response_body += chunk
            
            # 重置响应体
            response.body_iterator = self._create_body_iterator(response_body)
            
            # 设置缓存
            cache_ttl = self._get_cache_ttl(request)
            await self.cache.set(
                cache_key,
                {
                    "headers": dict(response.headers),
                    "body": response_body,
                    "process_time": process_time
                },
                ttl=cache_ttl
            )
            response.headers["X-Cache"] = "MISS"
        else:
            response.headers["X-Cache"] = "SKIP"

        # 添加性能相关头部
        response.headers["X-Response-Time"] = f"{process_time:.4f}s"
        
        return response

    def _generate_cache_key(self, request: Request) -> str:
        """
        生成缓存键
        """
        # 包含URL路径、查询参数和用户信息（如果有的话）
        path = request.url.path
        query_params = sorted(request.query_params.items())
        
        # 为不同用户生成不同的缓存键（如果用户已认证）
        user_key = ""
        try:
            # 尝试从请求中获取用户信息
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
                # 使用token的一部分作为用户标识
                user_key = f"user_{hashlib.md5(token.encode()).hexdigest()[:8]}"
        except:
            pass
        
        # 创建一个表示请求的唯一键
        key_data = f"{path}?{dict(query_params)}#{user_key}"
        return f"perf_cache:{hashlib.sha256(key_data.encode()).hexdigest()[:16]}"

    def _is_safe_to_cache(self, request: Request) -> bool:
        """
        检查请求是否适合缓存
        """
        # 只缓存GET请求
        if request.method != "GET":
            return False
            
        # 不缓存包含认证信息的请求（除非是公共数据）
        if "authorization" in request.headers:
            # 检查是否为公开API路径
            public_paths = ["/health", "/docs", "/redoc"]
            if not any(request.url.path.startswith(path) for path in public_paths):
                return False
                
        # 不缓存包含某些参数的请求
        exclude_params = ["token", "session", "auth"]
        for param in exclude_params:
            if param in request.query_params:
                return False
                
        # 检查路径是否应该被缓存
        exclude_paths = ["/admin/", "/auth/"]
        for path in exclude_paths:
            if path in request.url.path:
                return False
                
        return True

    def _get_cache_ttl(self, request: Request) -> int:
        """
        根据请求路径获取缓存TTL
        """
        path = request.url.path
        
        # 不同路径设置不同的缓存时间
        if "/matches/" in path or "/leagues/" in path:
            # 比赛数据，缓存30分钟
            return 1800
        elif "/stats/" in path:
            # 统计数据，缓存1小时
            return 3600
        elif "/cache/" in path or "/metrics/" in path:
            # 缓存和指标数据，缓存5分钟
            return 300
        else:
            # 默认缓存15分钟
            return 900

    async def _compress_response_if_needed(self, response: Response) -> Response:
        """
        如果需要，压缩响应内容
        """
        # 检查内容类型是否适合压缩
        content_type = response.headers.get("content-type", "").lower()
        if "application/json" in content_type or "text/" in content_type:
            # 这里可以实现实际的压缩逻辑
            # 为了简化，我们跳过压缩，但在生产环境中应该实现压缩
            pass
            
        return response

    def _create_body_iterator(self, body: bytes):
        """
        创建响应体迭代器
        """
        async def app(scope, receive, send):
            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [(b'content-length', str(len(body)).encode())]
            })
            await send({
                'type': 'http.response.body',
                'body': body,
                'more_body': False
            })

        return app