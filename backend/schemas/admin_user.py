"""
后台管理用户Schema定义
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AdminRoleEnum(str, Enum):
    """后台用户角色枚举"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    AUDITOR = "auditor"
    OPERATOR = "operator"


class AdminStatusEnum(str, Enum):
    """后台用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    LOCKED = "locked"


# ==================== 后台用户Schema ====================

class AdminUserBase(BaseModel):
    """后台用户基础Schema"""
    username: str = Field(..., min_length=3, max_length=80)
    email: EmailStr
    real_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    role: AdminRoleEnum = AdminRoleEnum.OPERATOR


class AdminUserCreate(AdminUserBase):
    """创建后台用户Schema"""
    password: str = Field(..., min_length=8, max_length=128)
    login_allowed_ips: Optional[List[str]] = None
    two_factor_enabled: bool = False
    remarks: Optional[str] = None
    
    @validator('password')
    def validate_password_strength(cls, v):
        """验证密码强度"""
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v


class AdminUserUpdate(BaseModel):
    """更新后台用户Schema"""
    email: Optional[EmailStr] = None
    real_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    role: Optional[AdminRoleEnum] = None
    status: Optional[AdminStatusEnum] = None
    login_allowed_ips: Optional[List[str]] = None
    two_factor_enabled: Optional[bool] = None
    remarks: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class AdminUserChangePassword(BaseModel):
    """修改密码Schema"""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """验证密码强度"""
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """验证两次密码是否一致"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v


class AdminUserResetPassword(BaseModel):
    """重置密码Schema（管理员操作）"""
    new_password: str = Field(..., min_length=8, max_length=128)
    must_change_password: bool = True
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """验证密码强度"""
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        return v


class AdminUserResponse(AdminUserBase):
    """后台用户响应Schema"""
    id: int
    status: AdminStatusEnum
    is_verified: bool
    two_factor_enabled: bool
    login_count: int
    last_login_at: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    failed_login_attempts: int
    locked_until: Optional[datetime] = None
    must_change_password: bool
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    remarks: Optional[str] = None
    
    class Config:
        from_attributes = True


class AdminUserListResponse(BaseModel):
    """后台用户列表响应Schema"""
    items: List[AdminUserResponse]
    total: int
    page: int
    size: int
    pages: int


class AdminUserDetailResponse(AdminUserResponse):
    """后台用户详情响应Schema（包含更多信息）"""
    login_allowed_ips: Optional[List[str]] = None
    password_expires_at: Optional[datetime] = None
    preferences: Dict[str, Any] = {}
    creator_name: Optional[str] = None  # 创建者名称


# ==================== 后台操作日志Schema ====================

class AdminOperationLogBase(BaseModel):
    """操作日志基础Schema"""
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None


class AdminOperationLogResponse(AdminOperationLogBase):
    """操作日志响应Schema"""
    id: int
    admin_id: int
    admin_name: Optional[str] = None  # 操作人员名称
    method: str
    path: str
    status_code: int
    ip_address: str
    created_at: datetime
    duration_ms: Optional[int] = None
    
    class Config:
        from_attributes = True


class AdminOperationLogListResponse(BaseModel):
    """操作日志列表响应Schema"""
    items: List[AdminOperationLogResponse]
    total: int
    page: int
    size: int
    pages: int


class AdminOperationLogDetailResponse(AdminOperationLogResponse):
    """操作日志详情响应Schema（包含完整信息）"""
    query_params: Dict[str, Any] = {}
    request_body: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    changes_before: Optional[Dict[str, Any]] = None
    changes_after: Optional[Dict[str, Any]] = None
    user_agent: Optional[str] = None


# ==================== 后台登录日志Schema ====================

class AdminLoginLogResponse(BaseModel):
    """登录日志响应Schema"""
    id: int
    admin_id: int
    admin_name: Optional[str] = None
    login_at: datetime
    login_ip: str
    success: bool
    failure_reason: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    device_type: Optional[str] = None
    os: Optional[str] = None
    browser: Optional[str] = None
    two_factor_used: bool
    ip_whitelisted: bool
    
    class Config:
        from_attributes = True


class AdminLoginLogListResponse(BaseModel):
    """登录日志列表响应Schema"""
    items: List[AdminLoginLogResponse]
    total: int
    page: int
    size: int
    pages: int


# ==================== 统计Schema ====================

class AdminUserStatsResponse(BaseModel):
    """后台用户统计Schema"""
    total_users: int
    active_users: int
    inactive_users: int
    suspended_users: int
    locked_users: int
    users_by_role: Dict[str, int]
    users_by_department: Dict[str, int]
    recent_logins: int  # 最近24小时登录人数
    two_factor_enabled_count: int


class AdminActivityStatsResponse(BaseModel):
    """后台活动统计Schema"""
    total_operations: int
    operations_by_action: Dict[str, int]
    operations_by_resource: Dict[str, int]
    failed_operations: int
    average_response_time: float
    peak_hours: List[Dict[str, Any]]  # 操作高峰时段
