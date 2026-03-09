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
try:
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
except ImportError:
    # 如果utils.exceptions不存在，则定义一些基本异常类
    class AuthenticationError(Exception):
        """认证错误"""
        pass

    class AuthorizationError(Exception):
        """授权错误"""
        pass

    class ValidationError(Exception):
        """验证错误"""
        pass

    class UserNotFoundError(Exception):
        """用户未找到错误"""
        pass

    class UserAlreadyExistsError(Exception):
        """用户已存在错误"""
        pass

    class AccountDisabledError(Exception):
        """账户禁用错误"""
        pass

    class InvalidTokenError(Exception):
        """无效令牌错误"""
        pass

    class PasswordStrengthError(Exception):
        """密码强度错误"""
        pass

    class TokenValidationError(Exception):
        """令牌验证错误"""
        pass

    class BusinessLogicError(Exception):
        """业务逻辑错误"""
        pass

    class DatabaseError(Exception):
        """数据库错误"""
        pass

    class ConfigurationError(Exception):
        """配置错误"""
        pass


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