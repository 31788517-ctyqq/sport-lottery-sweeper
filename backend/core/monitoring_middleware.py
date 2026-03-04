"""
监控中间件模块
用于收集API请求指标、性能数据和错误统计
"""
import time
import uuid
from datetime import datetime
from typing import Callable, Awaitable
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class MonitoringMiddleware(BaseHTTPMiddleware):
    """
    监控中间件，用于收集API请求指标
    """
    def __init__(self, app):
        super().__init__(app)
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录开始时间
        start_time = time.time()
        
        # 记录请求开始
        logger.info(
            f"REQUEST_START [ID: {request_id}] "
            f"{request.method} {request.url.path} "
            f"From: {request.client.host}:{request.client.port if request.client.port else 'unknown'}"
        )
        
        try:
            # 执行下一个中间件或路由处理器
            response = await call_next(request)
            
            # 计算响应时间
            process_time = time.time() - start_time
            self.total_response_time += process_time
            
            # 记录请求结束
            logger.info(
                f"REQUEST_END [ID: {request_id}] "
                f"{request.method} {request.url.path} "
                f"Status: {response.status_code} "
                f"Time: {process_time:.3f}s "
                f"Client: {request.client.host}"
            )
            
            # 增加计数
            self.request_count += 1
            
            if response.status_code >= 400:
                self.error_count += 1
                
            # 添加监控头部信息
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 计算响应时间
            process_time = time.time() - start_time
            self.total_response_time += process_time
            
            # 记录异常
            logger.error(
                f"REQUEST_ERROR [ID: {request_id}] "
                f"{request.method} {request.url.path} "
                f"Error: {str(e)} "
                f"Time: {process_time:.3f}s "
                f"Client: {request.client.host}",
                exc_info=True
            )
            
            # 增加计数
            self.request_count += 1
            self.error_count += 1
            
            # 重新抛出异常，让异常处理器处理
            raise