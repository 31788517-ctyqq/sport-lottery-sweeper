"""
用户相关数据模式
"""
from pydantic import BaseModel, EmailStr, Field
from pydantic_settings import SettingsConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserStatusEnum(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"


class UserTypeEnum(str, Enum):
    """用户类型枚举"""
    NORMAL = "normal"
    PREMIUM = "premium"
    ANALYST = "analyst"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserRoleEnum(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    ANALYST = "analyst"
    REGULAR_USER = "regular_user"
    GUEST = "guest"


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
    username: str = Field(..., min_length=3, max_length=80, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    first_name: Optional[str] = Field(None, max_length=50, description="名字")
    last_name: Optional[str] = Field(None, max_length=50, description="姓氏")
    nickname: Optional[str] = Field(None, max_length=80, description="昵称")
    bio: Optional[str] = Field(None, description="个人简介")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")
    phone: Optional[str] = Field(None, max_length=20, description="电话号码")
    country: Optional[str] = Field(None, max_length=100, description="国家")
    city: Optional[str] = Field(None, max_length=100, description="城市")
    role: UserRoleEnum = Field(default=UserRoleEnum.REGULAR_USER, description="用户角色")
    status: UserStatusEnum = Field(default=UserStatusEnum.ACTIVE, description="用户状态")
    is_verified: bool = Field(default=False, description="是否已验证")
    user_type: UserTypeEnum = Field(default=UserTypeEnum.NORMAL, description="用户类型")
    timezone: str = Field(default="UTC", max_length=50, description="时区")
    language: str = Field(default="zh", max_length=10, description="语言")


class UserCreate(UserBase):
    """
    创建用户模型
    """
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class UserUpdate(BaseModel):
    """
    更新用户模型
    """
    username: Optional[str] = Field(None, min_length=3, max_length=80, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    first_name: Optional[str] = Field(None, max_length=50, description="名字")
    last_name: Optional[str] = Field(None, max_length=50, description="姓氏")
    nickname: Optional[str] = Field(None, max_length=80, description="昵称")
    bio: Optional[str] = Field(None, description="个人简介")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")
    phone: Optional[str] = Field(None, max_length=20, description="电话号码")
    country: Optional[str] = Field(None, max_length=100, description="国家")
    city: Optional[str] = Field(None, max_length=100, description="城市")
    role: Optional[UserRoleEnum] = Field(None, description="用户角色")
    status: Optional[UserStatusEnum] = Field(None, description="用户状态")
    is_verified: Optional[bool] = Field(None, description="是否已验证")
    user_type: Optional[UserTypeEnum] = Field(None, description="用户类型")
    timezone: Optional[str] = Field(None, max_length=50, description="时区")
    language: Optional[str] = Field(None, max_length=10, description="语言")


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


class User(UserBase):
    """用户模型（包含ID和时间戳）"""
    id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    is_online: bool = Field(default=False, description="是否在线")
    login_count: int = Field(default=0, description="登录次数")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    last_activity_at: Optional[datetime] = Field(None, description="最后活动时间")
    followers_count: int = Field(default=0, description="粉丝数")
    following_count: int = Field(default=0, description="关注数")

    model_config = SettingsConfigDict()


class UserOut(UserBase):
    """用户输出模型（不包含敏感信息）"""
    id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    is_online: bool = Field(default=False, description="是否在线")
    login_count: int = Field(default=0, description="登录次数")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    last_activity_at: Optional[datetime] = Field(None, description="最后活动时间")
    followers_count: int = Field(default=0, description="粉丝数")
    following_count: int = Field(default=0, description="关注数")

    model_config = SettingsConfigDict()


# 为兼容多处引用的 UserListResponse 名称，添加别名
UserListResponse = UserList
