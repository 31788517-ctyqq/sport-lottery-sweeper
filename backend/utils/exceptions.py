#!/usr/bin/env python3
"""
自定义异常类模块
提供项目中使用的各种业务异常
"""

class AuthenticationError(Exception):
    """认证相关异常"""
    pass

class AuthorizationError(Exception):
    """授权相关异常"""
    pass

class ValidationError(Exception):
    """数据验证异常"""
    pass

class UserNotFoundError(Exception):
    """用户不存在异常"""
    pass

class UserAlreadyExistsError(Exception):
    """用户已存在异常"""
    pass

class AccountDisabledError(Exception):
    """账户禁用异常"""
    pass

class InvalidTokenError(Exception):
    """无效令牌异常"""
    pass

class PasswordStrengthError(Exception):
    """密码强度不足异常"""
    pass

class TokenValidationError(Exception):
    """令牌验证失败异常"""
    pass

class BusinessLogicError(Exception):
    """业务逻辑异常"""
    pass

class DatabaseError(Exception):
    """数据库操作异常"""
    pass

class ConfigurationError(Exception):
    """配置错误异常"""
    pass

# 导出所有异常类
__all__ = [
    "AuthenticationError", "AuthorizationError", "ValidationError",
    "UserNotFoundError", "UserAlreadyExistsError", "AccountDisabledError",
    "InvalidTokenError", "PasswordStrengthError", "TokenValidationError",
    "BusinessLogicError", "DatabaseError", "ConfigurationError"
]