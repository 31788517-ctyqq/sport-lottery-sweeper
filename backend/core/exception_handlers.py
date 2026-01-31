#!/usr/bin/env python3
"""
异常处理器模块
处理各种异常并返回标准化的API响应
"""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from .response import error_response

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    HTTP异常处理器
    
    Args:
        request: 请求对象
        exc: HTTP异常实例
        
    Returns:
        JSONResponse: 标准化的错误响应
    """
    error_data = error_response(
        message=exc.detail,
        code=exc.status_code,
        error_code="HTTP_ERROR"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_data
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    SQLAlchemy异常处理器
    
    Args:
        request: 请求对象
        exc: SQLAlchemy异常实例
        
    Returns:
        JSONResponse: 标准化的错误响应
    """
    error_data = error_response(
        message="数据库错误",
        code=500,
        error_code="DATABASE_ERROR",
        details={"original_error": str(exc)}
    )
    return JSONResponse(
        status_code=500,
        content=error_data
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    通用异常处理器
    
    Args:
        request: 请求对象
        exc: 异常实例
        
    Returns:
        JSONResponse: 标准化的错误响应
    """
    error_data = error_response(
        message="服务器内部错误",
        code=500,
        error_code="INTERNAL_SERVER_ERROR",
        details={"original_error": str(exc)}
    )
    return JSONResponse(
        status_code=500,
        content=error_data
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    验证异常处理器
    
    Args:
        request: 请求对象
        exc: 请求验证异常实例
        
    Returns:
        JSONResponse: 标准化的错误响应
    """
    # 提取验证错误详情
    details = []
    for error in exc.errors():
        detail = {
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "type": error.get("type")
        }
        details.append(detail)
    
    error_data = error_response(
        message="请求参数验证失败",
        code=422,
        error_code="VALIDATION_ERROR",
        details={"errors": details}
    )
    return JSONResponse(
        status_code=422,
        content=error_data
    )

__all__ = [
    "http_exception_handler",
    "sqlalchemy_exception_handler",
    "general_exception_handler",
    "validation_exception_handler"
]