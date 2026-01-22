"""
用户相关数据模式
"""
from pydantic import BaseModel, EmailStr, Field
from pydantic_settings import SettingsConfigDict
from typing import Optional
from datetime import datetime


class TokenData(BaseModel):
    """
    Token数据模型
    """
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """
    登录请求模型
    """
    username: str
    password: str


class RoleBase(BaseModel):
    """
    角色基础模型
    """
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """
    角色创建模型
    """
    pass


class RoleUpdate(BaseModel):
    """
    角色更新模型
    """
    name: Optional[str] = None
    description: Optional[str] = None


class RoleResponse(RoleBase):
    """
    角色响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = SettingsConfigDict()


class PermissionBase(BaseModel):
    """
    权限基础模型
    """
    name: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    """
    权限创建模型
    """
    pass


class PermissionUpdate(BaseModel):
    """
    权限更新模型
    """
    name: Optional[str] = None
    description: Optional[str] = None


class PermissionResponse(PermissionBase):
    """
    权限响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = SettingsConfigDict()


class UserBase(BaseModel):
    """
    用户基础模型
    """
    username: str
    email: EmailStr  # Use EmailStr for email validation
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """
    用户创建模型
    """
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long.")


class UserUpdate(BaseModel):
    """
    用户更新模型
    """
    email: Optional[EmailStr] = None  # Use EmailStr for email validation
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(UserBase):
    """
    用户响应模型
    """
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = SettingsConfigDict()


class UserList(BaseModel):
    """
    用户列表响应模型
    """
    items: list[UserResponse]
    total: int
    page: int
    size: int
    pages: int