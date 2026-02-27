#!/usr/bin/env python3
"""
用户相关的Pydantic模式定义
用于API请求和响应的数据验证
"""

from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

# 枚举定义
class UserStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class UserTypeEnum(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    VIP = "vip"

class AdminRoleEnum(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    OPERATOR = "operator"
    ANALYST = "analyst"

class AdminStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

# 基础响应模型
class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ==================== 普通用户模式 ====================

class UserBase(BaseModel):
    """用户基础信息"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    avatar: Optional[str] = Field(None, description="头像URL")

class UserCreate(UserBase):
    """创建用户请求模式"""
    password: str = Field(..., min_length=8, description="密码")
    confirm_password: str = Field(..., description="确认密码")
    
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        return v
    
    @field_validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('密码不匹配')
        return v

class UserUpdate(BaseModel):
    """更新用户请求模式"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    avatar: Optional[str] = Field(None, description="头像URL")
    password: Optional[str] = Field(None, min_length=8, description="新密码")
    confirm_password: Optional[str] = Field(None, description="确认新密码")
    
    @field_validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v and v != values['password']:
            raise ValueError('密码不匹配')
        return v

class UserResponse(UserBase):
    """用户响应模式"""
    id: int
    status: UserStatusEnum
    user_type: UserTypeEnum = UserTypeEnum.FREE
    email_verified: bool
    phone_verified: bool
    last_login_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserListResponse(BaseResponse):
    """用户列表响应模式"""
    users: List[UserResponse]
    total: int
    page: int
    size: int

# ==================== 管理员用户模式 ====================

class AdminUserBase(BaseModel):
    """管理员用户基础信息"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: str = Field(..., max_length=50, description="姓名")
    role: AdminRoleEnum = Field(..., description="角色")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    department: Optional[str] = Field(None, max_length=100, description="部门")
    permissions: Optional[List[str]] = Field(None, description="权限列表")

class AdminUserCreate(AdminUserBase):
    """创建管理员用户请求模式"""
    password: str = Field(..., min_length=8, description="密码")
    confirm_password: str = Field(..., description="确认密码")
    
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        return v
    
    @field_validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('密码不匹配')
        return v

class AdminUserUpdate(BaseModel):
    """更新管理员用户请求模式"""
    full_name: Optional[str] = Field(None, max_length=50, description="姓名")
    role: Optional[AdminRoleEnum] = Field(None, description="角色")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    department: Optional[str] = Field(None, max_length=100, description="部门")
    permissions: Optional[List[str]] = Field(None, description="权限列表")
    status: Optional[AdminStatusEnum] = Field(None, description="状态")
    password: Optional[str] = Field(None, min_length=8, description="新密码")
    confirm_password: Optional[str] = Field(None, description="确认新密码")
    
    @field_validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v and v != values['password']:
            raise ValueError('密码不匹配')
        return v

class AdminUserResponse(AdminUserBase):
    """管理员用户响应模式"""
    id: int
    status: AdminStatusEnum
    last_login_time: Optional[datetime]
    login_count: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    
    model_config = ConfigDict(from_attributes=True)

class AdminUserListResponse(BaseResponse):
    """管理员用户列表响应模式"""
    admins: List[AdminUserResponse]
    total: int
    page: int
    size: int

# ==================== 认证相关模式 ====================

class LoginRequest(BaseModel):
    """登录请求模式"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")

class LoginResponse(BaseResponse):
    """登录响应模式"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: UserResponse

class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模式"""
    refresh_token: str = Field(..., description="刷新令牌")

class ChangePasswordRequest(BaseModel):
    """修改密码请求模式"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, description="新密码")
    confirm_new_password: str = Field(..., description="确认新密码")
    
    @field_validator('confirm_new_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('新密码不匹配')
        return v

# ==================== 通用User类（兼容性导出）====================

# 为了兼容现有代码，将UserResponse别名为User
User = UserResponse


# ==================== 统计信息模式 ====================

class UserStatsResponse(BaseResponse):
    """用户统计信息响应模式"""
    total_users: int
    active_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    user_type_distribution: Dict[str, int]
    status_distribution: Dict[str, int]

class AdminStatsResponse(BaseResponse):
    """管理员统计信息响应模式"""
    total_admins: int
    active_admins: int
    new_admins_today: int
    new_admins_this_week: int
    new_admins_this_month: int
    role_distribution: Dict[str, int]
    status_distribution: Dict[str, int]


# ==================== 兼容性别名 ====================
# 为了兼容现有代码中的导入
AdminDataCreate = AdminUserCreate
AdminDataUpdate = AdminUserUpdate
AdminDataResponse = AdminUserResponse
AdminDataListResponse = AdminUserListResponse
# AI_WORKING: coder1 @2026-01-26 - 添加UserLogin别名以修复导入错误
UserLogin = LoginRequest
# AI_DONE: coder1 @2026-01-26 - 添加UserLogin别名以修复导入错误