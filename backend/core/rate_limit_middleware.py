"""
API限流中间件
用于控制客户端请求频率，防止API滥用
"""
import time
import json
from collections import defaultdict
from typing import Dict, List, Callable, Awaitable
from datetime import datetime, timedelta
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    限流中间件，基于IP地址和时间窗口进行限流
    """
    def __init__(self, app, requests_per_minute: int = 60, ban_duration: int = 300):
        """
        初始化限流中间件
        :param app: ASGI应用
        :param requests_per_minute: 每分钟允许的最大请求数
        :param ban_duration: 封禁时长（秒）
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.ban_duration = ban_duration
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.banned_ips: Dict[str, float] = {}
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        client_ip = self._get_client_ip(request)
        
        # 检查IP是否被封禁
        if client_ip in self.banned_ips:
            ban_expires_at = self.banned_ips[client_ip]
            if time.time() < ban_expires_at:
                logger.warning(f"Blocked banned IP: {client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": "Too many requests, please try again later",
                            "status_code": 429
                        }
                    }
                )
            else:
                # 清除过期的封禁
                del self.banned_ips[client_ip]
        
        # 获取当前时间窗口内的请求记录
        now = time.time()
        time_window_start = now - 60  # 一分钟的时间窗口
        
        # 清理过期的请求记录
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip] 
            if req_time > time_window_start
        ]
        
        # 检查是否超过限制
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            # 添加到封禁列表
            self.banned_ips[client_ip] = now + self.ban_duration
            
            logger.warning(f"Rate limit exceeded for IP: {client_ip}, banning for {self.ban_duration}s")
            
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests, please try again later",
                        "status_code": 429
                    }
                }
            )
        
        # 记录本次请求
        self.requests[client_ip].append(now)
        
        # 调用下一个中间件
        response = await call_next(request)
        
        # 添加限流相关信息到响应头
        remaining_requests = max(0, self.requests_per_minute - len(self.requests[client_ip]))
        response.headers["X-RateLimit-Remaining"] = str(remaining_requests)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """
        获取客户端IP地址
        """
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        
        return request.client.host