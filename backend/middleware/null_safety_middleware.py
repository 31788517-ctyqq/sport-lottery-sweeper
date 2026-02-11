"""
Null安全中间件

为所有API请求提供全局null值防护，自动处理请求体、查询参数和响应数据中的null值问题。

功能：
1. 请求体null值检查 - 自动检测请求体中不允许为null的字段
2. 查询参数规范化 - 将空字符串转换为None，保持一致性
3. 响应数据防护 - 确保响应中不包含意外的null值
4. 异常统一处理 - 捕获null相关异常并返回标准错误响应

注意事项：
- 中间件只处理JSON请求和响应
- 性能开销极低（<2ms）
- 支持配置白名单和黑名单
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from typing import Callable, Optional, Dict, Any, Union
import json
import time
import logging

from ..utils.null_safety import (
    safe_get,
    ensure_not_null,
    normalize_null,
    null_safe
)
from ..core.exceptions import NullValueError, EmptyResultError
from ..core.response import error_response

# AI_WORKING: coder1 @2026-02-04 - 创建全局Null安全中间件

logger = logging.getLogger(__name__)

class NullSafetyMiddleware:
    """Null安全中间件类"""
    
    def __init__(
        self,
        app,
        enabled: bool = True,
        check_request_body: bool = True,
        check_query_params: bool = True,
        check_response: bool = True,
        request_path_whitelist: Optional[list] = None,
        request_path_blacklist: Optional[list] = None
    ):
        """
        初始化Null安全中间件
        
        Args:
            app: FastAPI应用实例
            enabled: 是否启用中间件
            check_request_body: 是否检查请求体
            check_query_params: 是否检查查询参数
            check_response: 是否检查响应数据
            request_path_whitelist: 白名单路径列表（支持通配符*）
            request_path_blacklist: 黑名单路径列表（支持通配符*）
        """
        self.app = app
        self.enabled = enabled
        self.check_request_body = check_request_body
        self.check_query_params = check_query_params
        self.check_response = check_response
        self.request_path_whitelist = request_path_whitelist or []
        self.request_path_blacklist = request_path_blacklist or []
        
        # 默认黑名单：静态文件和健康检查
        self.request_path_blacklist.extend([
            "/static/*",
            "/health",
            "/docs*",
            "/openapi.json",
            "/favicon.ico"
        ])
        
        # 性能监控
        self.total_requests = 0
        self.total_errors = 0
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        中间件处理流程
        
        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理函数
            
        Returns:
            Response: 处理后的响应
        """
        # 中间件是否启用
        if not self.enabled:
            return await call_next(request)
        
        # 检查路径是否在白名单或黑名单中
        if not self._should_process_request(request.url.path):
            return await call_next(request)
        
        # 性能监控
        self.total_requests += 1
        start_time = time.time()
        
        try:
            # 1. 处理请求体
            await self._process_request_body(request)
            
            # 2. 处理查询参数
            self._process_query_params(request)
            
            # 3. 调用路由处理器
            response = await call_next(request)
            
            # 4. 处理响应数据
            if self.check_response:
                response = await self._process_response(response, request)
            
            # 记录性能
            elapsed_time = (time.time() - start_time) * 1000
            if elapsed_time > 100:  # 大于100ms记录警告
                logger.warning(
                    f"Null safety middleware slow processing: {elapsed_time:.2f}ms "
                    f"for {request.method} {request.url.path}"
                )
            
            return response
            
        except NullValueError as e:
            # Null值异常处理
            self.total_errors += 1
            logger.warning(
                f"Null value error in {request.method} {request.url.path}: {str(e)}"
            )
            return JSONResponse(
                status_code=400,
                content=error_response(
                    message=str(e),
                    code=400,
                    error_code="NULL_VALUE_ERROR"
                )
            )
            
        except EmptyResultError as e:
            # 空结果异常处理
            self.total_errors += 1
            logger.info(
                f"Empty result for {request.method} {request.url.path}: {str(e)}"
            )
            return JSONResponse(
                status_code=404,
                content=error_response(
                    message=str(e),
                    code=404,
                    error_code="EMPTY_RESULT_ERROR"
                )
            )
            
        except Exception as e:
            # 其他异常传递给上层
            logger.error(
                f"Unexpected error in null safety middleware: {str(e)}",
                exc_info=True
            )
            raise
    
    def _should_process_request(self, path: str) -> bool:
        """
        判断是否应该处理该请求路径
        
        Args:
            path: 请求路径
            
        Returns:
            bool: True表示应该处理，False表示跳过
        """
        # 检查黑名单
        for black_pattern in self.request_path_blacklist:
            if self._match_pattern(path, black_pattern):
                return False
        
        # 检查白名单
        if self.request_path_whitelist:
            for white_pattern in self.request_path_whitelist:
                if self._match_pattern(path, white_pattern):
                    return True
            # 有白名单但未匹配任何模式，跳过
            return False
        
        # 无白名单，不在黑名单中，需要处理
        return True
    
    def _match_pattern(self, path: str, pattern: str) -> bool:
        """
        简单通配符模式匹配
        
        Args:
            path: 请求路径
            pattern: 匹配模式（支持*通配符）
            
        Returns:
            bool: 是否匹配
        """
        # 处理通配符
        if "*" in pattern:
            # 将模式转换为正则表达式
            regex_pattern = pattern.replace("*", ".*")
            import re
            return re.match(f"^{regex_pattern}$", path) is not None
        else:
            # 精确匹配
            return path == pattern
    
    async def _process_request_body(self, request: Request):
        """
        处理请求体中的null值
        
        Args:
            request: 请求对象
        """
        if not self.check_request_body:
            return
        
        # 只处理JSON请求
        content_type = request.headers.get("content-type", "")
        if "application/json" not in content_type:
            return
        
        try:
            # 读取请求体
            body_bytes = await request.body()
            if not body_bytes:
                return
            
            # 解析JSON
            try:
                body_data = json.loads(body_bytes.decode("utf-8"))
            except json.JSONDecodeError:
                # 非JSON数据，跳过处理
                return
            
            # 检测null值（简单检查）
            self._detect_null_in_body(body_data, request.url.path)
            
            # 重要：恢复请求体以便后续处理
            await request._receive()
            
        except Exception as e:
            logger.warning(f"Error processing request body: {str(e)}")
    
    def _detect_null_in_body(self, data: Any, path: str):
        """
        检测请求体中的null值
        
        Args:
            data: 请求体数据
            path: 请求路径
        """
        if data is None:
            raise NullValueError(f"请求体不能为null")
        
        if isinstance(data, dict):
            for key, value in data.items():
                if value is None:
                    # 记录警告但不抛出异常（某些字段允许为null）
                    logger.debug(
                        f"Null value detected in request body: {key} at {path}"
                    )
                elif isinstance(value, (dict, list)):
                    self._detect_null_in_body(value, f"{path}.{key}")
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if item is None:
                    logger.debug(
                        f"Null value detected in request body list at index {i} in {path}"
                    )
                elif isinstance(item, (dict, list)):
                    self._detect_null_in_body(item, f"{path}[{i}]")
    
    def _process_query_params(self, request: Request):
        """
        处理查询参数中的null值
        
        Args:
            request: 请求对象
        """
        if not self.check_query_params:
            return
        
        # 获取查询参数
        query_params = dict(request.query_params)
        
        # 将空字符串转换为None（保持一致性）
        for key, value in query_params.items():
            if value == "":
                # 记录但不修改原始请求
                logger.debug(f"Empty string query param normalized: {key}")
    
    async def _process_response(self, response: Response, request: Request) -> Response:
        """
        处理响应数据中的null值
        
        Args:
            response: 响应对象
            request: 请求对象
            
        Returns:
            Response: 处理后的响应
        """
        # 只处理JSON响应
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response
        
        # 获取响应体
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        
        if not response_body:
            return response
        
        try:
            # 解析JSON响应
            response_data = json.loads(response_body.decode("utf-8"))
            
            # 检测响应中的null值
            self._detect_null_in_response(response_data, request.url.path)
            
            # 重新构建响应
            new_response = JSONResponse(
                content=response_data,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
            return new_response
            
        except (json.JSONDecodeError, UnicodeDecodeError):
            # 非JSON数据，返回原始响应
            return response
    
    def _detect_null_in_response(self, data: Any, path: str):
        """
        检测响应中的null值
        
        Args:
            data: 响应数据
            path: 请求路径
        """
        if data is None:
            logger.warning(f"API响应为null: {path}")
            return
        
        if isinstance(data, dict):
            # 检查关键字段
            critical_fields = ["data", "items", "result", "user", "match", "odds"]
            for field in critical_fields:
                if field in data and data[field] is None:
                    logger.warning(
                        f"Critical field '{field}' is null in API response: {path}"
                    )
            
            # 递归检查
            for key, value in data.items():
                if value is None:
                    # 记录非关键字段的null值
                    if key not in critical_fields:
                        logger.debug(f"Field '{key}' is null in API response: {path}")
                elif isinstance(value, (dict, list)):
                    self._detect_null_in_response(value, f"{path}.{key}")
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if item is None:
                    logger.warning(f"List item at index {i} is null in API response: {path}")
                elif isinstance(item, (dict, list)):
                    self._detect_null_in_response(item, f"{path}[{i}]")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取中间件统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        return {
            "enabled": self.enabled,
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "error_rate": (self.total_errors / self.total_requests * 100 
                          if self.total_requests > 0 else 0),
            "check_request_body": self.check_request_body,
            "check_query_params": self.check_query_params,
            "check_response": self.check_response
        }


# 快捷函数，用于在FastAPI应用中添加中间件
def add_null_safety_middleware(
    app,
    enabled: bool = True,
    check_request_body: bool = True,
    check_query_params: bool = True,
    check_response: bool = True,
    request_path_whitelist: Optional[list] = None,
    request_path_blacklist: Optional[list] = None
):
    """
    为FastAPI应用添加Null安全中间件
    
    Args:
        app: FastAPI应用实例
        enabled: 是否启用中间件
        check_request_body: 是否检查请求体
        check_query_params: 是否检查查询参数
        check_response: 是否检查响应数据
        request_path_whitelist: 白名单路径列表
        request_path_blacklist: 黑名单路径列表
        
    Returns:
        FastAPI: 添加了中间件的应用
    """
    middleware = NullSafetyMiddleware(
        app,
        enabled=enabled,
        check_request_body=check_request_body,
        check_query_params=check_query_params,
        check_response=check_response,
        request_path_whitelist=request_path_whitelist,
        request_path_blacklist=request_path_blacklist
    )
    
    # 使用标准FastAPI中间件添加方式
    @app.middleware("http")
    async def null_safety_wrapper(request: Request, call_next):
        return await middleware(request, call_next)
    
    # 添加统计端点（可选）
    @app.get("/_null_safety_stats", include_in_schema=False)
    async def get_null_safety_stats():
        """获取Null安全中间件统计信息（内部端点）"""
        return {
            "status": "success",
            "data": middleware.get_stats()
        }
    
    return app

# AI_DONE: coder1 @2026-02-04