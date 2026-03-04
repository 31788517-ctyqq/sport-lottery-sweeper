"""
请求日志中间件
"""
from fastapi import Request
from fastapi.responses import Response
import time
import logging

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    请求日志中间件
    记录请求的基本信息和处理时间
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)
        start_time = time.time()

        # 记录请求开始
        logger.info(f"Request: {request.method} {request.url}")

        # 创建响应时间记录器包装器
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                process_time = time.time() - start_time
                message.setdefault("headers", [])
                message["headers"].append([b"X-Process-Time", str(process_time).encode("latin-1")])
                logger.info(f"Response status: {message['status']}, Process time: {process_time:.4f}s")
            await send(message)

        # 调用下一个中间件或应用
        await self.app(scope, receive, send_wrapper)