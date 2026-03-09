#!/usr/bin/env python3
"""
认证相关 Pydantic Schema 定义
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional

class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str = "用户名或邮箱"
    password: str = "密码"
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "admin",
                "password": "password123"
            }
        }
    )

class RegisterRequest(BaseModel):
    """注册请求模型"""
    username: str = "用户名"
    email: str = "邮箱地址"
    password: str = "密码"
    nickname: Optional[str] = "昵称（可选）"
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "newuser",
                "email": "user@example.com",
                "password": "password123",
                "nickname": "新用户"
            }
        }
    )

class AuthResponse(BaseModel):
    """认证响应模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: dict
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user_info": {
                    "id": 1,
                    "username": "admin",
                    "email": "admin@example.com",
                    "roles": ["admin"]
                }
            }
        }
    )

# 导出所有schema
__all__ = ['LoginRequest', 'RegisterRequest', 'AuthResponse']