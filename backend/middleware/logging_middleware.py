from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import time
import logging
from typing import Dict, Any

from backend.database import get_db
from backend.models.log_entry import LogEntry

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    日志记录中间件，用于记录API请求和响应
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 记录请求
        request_id = f"{int(start_time)}-{hash(request.url.path) % 10000}"
        logger.info(f"[{request_id}] {request.method} {request.url.path}")
        
        try:
            response: Response = await call_next(request)
        except Exception as e:
            # 记录异常
            duration = time.time() - start_time
            await self._save_log_entry(
                level="ERROR",
                module=f"API.{request.url.path}",
                message=f"Request failed: {str(e)}",
                details={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": 500,
                    "duration": duration,
                    "request_id": request_id,
                    "client_host": request.client.host,
                    "user_agent": request.headers.get("user-agent")
                }
            )
            raise e
        
        # 计算请求耗时
        duration = time.time() - start_time
        
        # 记录响应
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
            
        # 恢复响应体
        response.body_iterator = iter([response_body])
        
        # 确定日志级别
        log_level = "INFO"
        if response.status_code >= 500:
            log_level = "ERROR"
        elif response.status_code >= 400:
            log_level = "WARNING"
            
        # 保存日志记录
        await self._save_log_entry(
            level=log_level,
            module=f"API.{request.url.path}",
            message=f"Request completed",
            details={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration": duration,
                "request_id": request_id,
                "client_host": request.client.host,
                "user_agent": request.headers.get("user-agent")
            }
        )
        
        return response

    async def _save_log_entry(self, level: str, module: str, message: str, details: Dict[str, Any]):
        """
        保存日志记录到数据库
        """
        try:
            db_gen = get_db()
            db = next(db_gen)
            
            log_entry = LogEntry(
                timestamp=datetime.utcnow(),
                level=level,
                module=module,
                message=message,
                details=details
            )
            
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
            
        except Exception as e:
            logger.error(f"Failed to save log entry: {str(e)}")
        finally:
            try:
                db.close()
            except:
                pass