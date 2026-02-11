#!/usr/bin/env python3
"""
核心异常类模块
提供项目中使用的各种业务异常
"""

class ValidationException(Exception):
    """数据验证异常"""
    pass

class NotFoundException(Exception):
    """资源未找到异常"""
    pass

class BusinessException(Exception):
    """业务逻辑异常"""
    pass

# AI_WORKING: coder1 @2026-02-04 - 添加null值相关异常类
class NullValueError(BusinessException):
    """Null值异常 - 当遇到不允许为null的值时为null时抛出"""
    pass

class EmptyResultError(BusinessException):
    """空结果异常 - 当查询结果为空时抛出"""
    pass
# AI_DONE: coder1 @2026-02-04

# 为了兼容，也导出其他常见异常
from ..utils.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    UserNotFoundError,
    UserAlreadyExistsError,
    AccountDisabledError,
    InvalidTokenError,
    PasswordStrengthError,
    TokenValidationError,
    BusinessLogicError,
    DatabaseError,
    ConfigurationError
)

__all__ = [
    "ValidationException",
    "NotFoundException", 
    "BusinessException",
    "NullValueError",
    "EmptyResultError",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
    "UserNotFoundError",
    "UserAlreadyExistsError",
    "AccountDisabledError",
    "InvalidTokenError",
    "PasswordStrengthError",
    "TokenValidationError",
    "BusinessLogicError",
    "DatabaseError",
    "ConfigurationError"
]