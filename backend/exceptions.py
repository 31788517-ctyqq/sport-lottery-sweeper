"""
异常处理模块
定义自定义异常和全局异常处理器
"""
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging
import traceback

logger = logging.getLogger(__name__)


class BaseAPIException(Exception):
    """
    基础API异常类
    """
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "Internal server error",
        error_code: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        self.data = data or {}


class AuthenticationError(BaseAPIException):
    """认证错误"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTH_ERROR"
        )


class AuthorizationError(BaseAPIException):
    """授权错误"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="AUTHZ_ERROR"
        )


class ValidationException(BaseAPIException):
    """验证错误"""
    def __init__(self, detail: str = "Validation error", errors: Optional[list] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
            data={"errors": errors} if errors else {}
        )


class NotFoundException(BaseAPIException):
    """资源未找到错误"""
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found",
            error_code="NOT_FOUND"
        )


class ConflictException(BaseAPIException):
    """资源冲突错误"""
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="CONFLICT"
        )


class RateLimitException(BaseAPIException):
    """速率限制错误"""
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT"
        )


class ExternalAPIError(BaseAPIException):
    """外部API错误"""
    def __init__(self, detail: str = "External API error"):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
            error_code="EXTERNAL_API_ERROR"
        )


class CrawlerException(BaseAPIException):
    """爬虫错误"""
    def __init__(self, detail: str = "Crawler error", data: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="CRAWLER_ERROR",
            data=data
        )


class DatabaseException(BaseAPIException):
    """数据库错误"""
    def __init__(self, detail: str = "Database error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR"
        )


class BusinessException(BaseAPIException):
    """业务逻辑错误"""
    def __init__(self, detail: str = "Business logic error"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="BUSINESS_ERROR"
        )


def create_error_response(
    status_code: int,
    detail: str,
    error_code: Optional[str] = None,
    request_id: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    创建标准错误响应
    """
    response = {
        "success": False,
        "error": {
            "code": error_code or "UNKNOWN_ERROR",
            "message": detail,
            "status_code": status_code
        }
    }
    
    if data:
        response["error"]["data"] = data
    
    if request_id:
        response["request_id"] = request_id
    
    return response


async def base_exception_handler(request: Request, exc: BaseAPIException):
    """
    基础异常处理器
    """
    request_id = getattr(request.state, "request_id", None)
    
    logger.error(
        f"API Exception: {exc.__class__.__name__} - {exc.detail} "
        f"[Status: {exc.status_code}] [ID: {request_id}]"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            detail=exc.detail,
            error_code=exc.error_code,
            request_id=request_id,
            data=exc.data
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    请求验证异常处理器
    """
    request_id = getattr(request.state, "request_id", None)
    
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation Error: {str(errors)} [ID: {request_id}]"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Validation error",
            error_code="VALIDATION_ERROR",
            request_id=request_id,
            data={"errors": errors}
        )
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    通用异常处理器
    """
    request_id = getattr(request.state, "request_id", None)
    
    # 记录完整堆栈信息
    error_trace = traceback.format_exc()
    logger.error(
        f"Unhandled Exception: {str(exc)} "
        f"[Type: {exc.__class__.__name__}] [ID: {request_id}]\n"
        f"Traceback:\n{error_trace}"
    )
    
    # 生产环境隐藏详细错误信息
    detail = "Internal server error"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="INTERNAL_ERROR",
            request_id=request_id
        )
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    HTTP异常处理器
    """
    request_id = getattr(request.state, "request_id", None)
    
    logger.warning(
        f"HTTP Exception: {exc.detail} [Status: {exc.status_code}] [ID: {request_id}]"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            detail=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
            request_id=request_id
        )
    )


def setup_exception_handlers(app: FastAPI):
    """
    设置所有异常处理器
    """
    # 注册自定义异常处理器
    app.add_exception_handler(BaseAPIException, base_exception_handler)
    app.add_exception_handler(AuthenticationError, base_exception_handler)
    app.add_exception_handler(AuthorizationError, base_exception_handler)
    app.add_exception_handler(ValidationException, base_exception_handler)
    app.add_exception_handler(NotFoundException, base_exception_handler)
    app.add_exception_handler(ConflictException, base_exception_handler)
    app.add_exception_handler(RateLimitException, base_exception_handler)
    app.add_exception_handler(ExternalAPIError, base_exception_handler)
    app.add_exception_handler(CrawlerException, base_exception_handler)
    app.add_exception_handler(DatabaseException, base_exception_handler)
    app.add_exception_handler(BusinessException, base_exception_handler)
    
    # 注册FastAPI内置异常处理器
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    
    # 注册通用异常处理器（最后注册，作为兜底）
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("异常处理器配置完成")


# 上下文管理器用于优雅处理异常
class ExceptionContext:
    """
    异常上下文管理器
    用于在代码块中统一处理异常
    """
    
    def __init__(self, resource: str = "操作", log_errors: bool = True):
        self.resource = resource
        self.log_errors = log_errors
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            if self.log_errors:
                logger.error(f"{self.resource}失败: {str(exc_val)}")
            
            # 根据异常类型转换为API异常
            if exc_type == ValueError:
                raise ValidationException(str(exc_val))
            elif exc_type == PermissionError:
                raise AuthorizationError(str(exc_val))
            elif exc_type == FileNotFoundError:
                raise NotFoundException(f"{self.resource}未找到")
            else:
                # 其他异常转换为业务异常
                raise BusinessException(str(exc_val))
        
        return True  # 抑制异常传播