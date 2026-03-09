#!/usr/bin/env python3
"""
用户相关 Pydantic Schema 定义
"""

from pydantic import BaseModel, Field, validator, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime

# 基础响应模型
class MessageResponse(BaseModel):
    """消息响应模型"""
    message: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "操作成功"
            }
        }
    )

class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int

# 用户相关 Schema
class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description="手机号")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")

class UserCreate(UserBase):
    """创建用户请求模型"""
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度至少6位')
        return v

class UserUpdate(BaseModel):
    """更新用户请求模型"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    phone: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description="手机号")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    avatar: Optional[str] = Field(None, description="头像URL")

class UserLogin(BaseModel):
    """用户登录请求模型"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")

class UserRegister(BaseModel):
    """用户注册请求模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    
    @validator('username')
    def validate_username(cls, v):
        import re
        # 格式验证（字母、数字、下划线）
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        # 保留字检查
        reserved_words = ['admin', 'root', 'system', 'test', 'guest']
        if v.lower() in reserved_words:
            raise ValueError(f'用户名不能使用保留字: {v}')
        return v

class UserResponse(BaseModel):
    """用户信息响应模型"""
    id: int
    username: str
    email: str
    nickname: Optional[str]
    avatar: Optional[str]
    phone: Optional[str]
    bio: Optional[str]
    status: str
    email_verified: bool
    phone_verified: bool
    last_login_time: Optional[datetime]
    last_login_ip: Optional[str]
    login_count: int
    created_at: datetime
    updated_at: datetime
    roles: List[str]
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "nickname": "管理员",
                "avatar": "https://example.com/avatar.jpg",
                "phone": "13800138000",
                "bio": "系统管理员",
                "status": "active",
                "email_verified": True,
                "phone_verified": True,
                "last_login_time": "2024-01-25T10:30:00Z",
                "last_login_ip": "127.0.0.1",
                "login_count": 100,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-25T10:30:00Z",
                "roles": ["admin", "moderator"]
            }
        }
    )

class UserListResponse(BaseModel):
    """用户列表响应模型"""
    items: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int

class TokenResponse(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {
                    "id": 1,
                    "username": "admin",
                    "email": "admin@example.com"
                }
            }
        }
    )

# 导出所有schema
__all__ = [
    'MessageResponse', 'PaginatedResponse',
    'UserBase', 'UserCreate', 'UserUpdate', 'UserLogin', 'UserRegister',
    'UserResponse', 'UserListResponse', 'TokenResponse'
]