"""
用户数据模型
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, 
    ForeignKey, Float, Text, Enum, CheckConstraint, Index, Table, JSON
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
import enum

from sqlalchemy.ext.mutable import MutableDict
from .base import Base, BaseAuditModel, BaseFullModel

# 定义用户-角色关联表
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), default=func.now(), nullable=False)
)

# 定义角色-权限关联表
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), default=func.now(), nullable=False)
)

# 用户状态枚举
class UserStatusEnum(enum.Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"

# 用户类型枚举
class UserTypeEnum(enum.Enum):
    """用户类型枚举"""
    NORMAL = "normal"        # 普通用户
    PREMIUM = "premium"      # 高级用户
    ANALYST = "analyst"      # 分析师
    ADMIN = "admin"          # 管理员
    SUPER_ADMIN = "super_admin"  # 超级管理员

class UserRoleEnum(enum.Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    ANALYST = "analyst"
    REGULAR_USER = "regular_user"
    GUEST = "guest"

class User(BaseAuditModel):
    """
    用户模型
    """
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # 添加此选项以允许扩展已存在的表
    
    # 基本信息
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # 个人信息
    first_name = Column(String(50), nullable=True, index=True)
    last_name = Column(String(50), nullable=True, index=True)
    nickname = Column(String(80), nullable=True, index=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # 联系信息
    phone = Column(String(20), nullable=True, index=True)
    country = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    
    # 账户状态
    role = Column(Enum(UserRoleEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), default=UserRoleEnum.REGULAR_USER, nullable=False, index=True)
    status = Column(Enum(UserStatusEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), default=UserStatusEnum.ACTIVE, nullable=False, index=True)
    is_verified = Column(Boolean, default=False, nullable=False, index=True)
    is_online = Column(Boolean, default=False, nullable=False, index=True)
    user_type = Column(Enum(UserTypeEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), default=UserTypeEnum.NORMAL, nullable=False, index=True)
    
    # 偏好设置
    timezone = Column(String(50), default="UTC", nullable=False, index=True)
    language = Column(String(10), default="zh", nullable=False, index=True)
    notification_preferences = Column(Text, default='{}', nullable=False)
    
    # 统计信息
    login_count = Column(Integer, default=0, nullable=False, index=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True, index=True)
    last_activity_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # 社交信息
    followers_count = Column(Integer, default=0, nullable=False, index=True)
    following_count = Column(Integer, default=0, nullable=False, index=True)
    
    # 外部数据
    external_id = Column(String(100), nullable=True, index=True)  # 外部系统ID
    external_source = Column(String(50), nullable=True, index=True)  # 外部数据来源
    
    # 配置信息
    config = Column(MutableDict.as_mutable(JSON), default=lambda: {}, nullable=False)  # 用户配置
    
    # 关系
    login_logs = relationship("UserLoginLog", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("UserSubscription", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("UserPrediction", back_populates="user", cascade="all, delete-orphan")
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    
    # 索引
    __table_args__ = (
        Index('idx_users_status_role', 'status', 'role'),
        Index('idx_users_country_city', 'country', 'city'),
        Index('idx_users_created_at', 'created_at'),
        {'extend_existing': True}  # 确保支持表扩展
    )

class Role(BaseFullModel):
    """
    角色模型
    """
    __tablename__ = "roles"
    __table_args__ = {'extend_existing': True}  # 添加此选项以允许扩展已存在的表
    
    name = Column(String(50), unique=True, nullable=False, index=True)
    code = Column(String(30), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # 权限关联
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
    users = relationship("User", secondary="user_roles", back_populates="roles")
    
    __table_args__ = (
        Index('idx_roles_active', 'is_active'),
        {'extend_existing': True}  # 确保支持表扩展
    )

class Permission(BaseFullModel):
    """
    权限模型
    """
    __tablename__ = "permissions"
    __table_args__ = {'extend_existing': True}  # 添加此选项以允许扩展已存在的表
    
    name = Column(String(50), unique=True, nullable=False, index=True)
    code = Column(String(30), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    resource = Column(String(50), nullable=False, index=True)  # 资源类型
    action = Column(String(50), nullable=False, index=True)    # 操作类型
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # 角色关联
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")
    
    __table_args__ = (
        Index('idx_permissions_resource_action', 'resource', 'action'),
        Index('idx_permissions_active', 'is_active'),
        {'extend_existing': True}  # 确保支持表扩展
    )

class UserLoginLog(Base):
    """
    用户登录日志模型
    """
    __tablename__ = "user_login_logs"
    __table_args__ = {'extend_existing': True}  # 添加此选项以允许扩展已存在的表
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    login_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    login_ip = Column(String(45), nullable=True, index=True)  # 支持IPv6
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, default=True, nullable=False, index=True)
    failure_reason = Column(String(255), nullable=True, index=True)
    
    # 地理位置信息
    country = Column(String(100), nullable=True, index=True)
    region = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    
    # 设备信息
    device_type = Column(String(50), nullable=True, index=True)  # mobile, tablet, desktop
    device_name = Column(String(100), nullable=True)
    os = Column(String(50), nullable=True, index=True)  # 操作系统
    browser = Column(String(50), nullable=True, index=True)  # 浏览器
    
    # 关系
    user = relationship("User", back_populates="login_logs")
    
    # 索引
    __table_args__ = (
        Index('idx_login_logs_user_time', 'user_id', 'login_at'),
        Index('idx_login_logs_ip_time', 'login_ip', 'login_at'),
        Index('idx_login_logs_success_time', 'success', 'login_at'),
        {'extend_existing': True}  # 确保支持表扩展
    )

class UserActivity(Base):
    """
    用户活动日志模型
    """
    __tablename__ = "user_activities"
    __table_args__ = {'extend_existing': True}  # 添加此选项以允许扩展已存在的表
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    activity_type = Column(String(100), nullable=False, index=True)  # 登录、浏览、下单等
    activity_time = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # 资源信息
    resource_type = Column(String(50), nullable=True, index=True)  # match, league, prediction等
    resource_id = Column(String(50), nullable=True, index=True)    # 资源ID
    resource_name = Column(String(255), nullable=True, index=True) # 资源名称
    
    # 请求信息
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    endpoint = Column(String(255), nullable=True, index=True)      # 请求端点
    http_method = Column(String(10), nullable=True, index=True)    # GET, POST等
    http_status = Column(Integer, nullable=True, index=True)       # HTTP状态码
    
    # 附加信息
    details = Column(MutableDict.as_mutable(Text), default=lambda: {}, nullable=False)  # 额外的详细信息
    
    # 关系
    user = relationship("User", back_populates="activities")
    
    # 索引
    __table_args__ = (
        Index('idx_activities_user_time', 'user_id', 'activity_time'),
        Index('idx_activities_type_time', 'activity_type', 'activity_time'),
        Index('idx_activities_resource', 'resource_type', 'resource_id'),
        {'extend_existing': True}  # 确保支持表扩展
    )

class UserSubscription(Base):
    """
    用户订阅模型
    """
    __tablename__ = "user_subscriptions"
    __table_args__ = {'extend_existing': True}  # 添加此选项以允许扩展已存在的表
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    subscription_type = Column(String(50), nullable=False, index=True)  # match_updates, league_news, predictions等
    target_id = Column(String(50), nullable=False, index=True)  # 订阅目标ID (联赛ID、球队ID等)
    target_name = Column(String(255), nullable=False, index=True)  # 订阅目标名称
    
    # 通知设置
    notification_enabled = Column(Boolean, default=True, nullable=False)
    email_notifications = Column(Boolean, default=True, nullable=False)
    push_notifications = Column(Boolean, default=False, nullable=False)
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    subscribed_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)
    
    # 偏好设置
    preferences = Column(Text, default='{}', nullable=False)  # 特定于订阅的偏好设置
    
    # 关系
    user = relationship("User", back_populates="subscriptions")
    
    # 索引
    __table_args__ = (
        Index('idx_subscriptions_user_type', 'user_id', 'subscription_type'),
        Index('idx_subscriptions_target_active', 'target_id', 'is_active'),
        Index('idx_subscriptions_active_type', 'is_active', 'subscription_type'),
        {'extend_existing': True}  # 确保支持表扩展
    )

# 初始化系统角色和权限
SYSTEM_ROLES = [
    {
        "name": "超级管理员",
        "code": "super_admin",
        "description": "系统超级管理员，拥有所有权限",
        "level": 0,
        "is_default": False,
        "is_system": True
    },
    {
        "name": "管理员",
        "code": "admin",
        "description": "系统管理员，拥有大部分管理权限",
        "level": 1,
        "is_default": False,
        "is_system": True
    },
    {
        "name": "分析师",
        "code": "analyst",
        "description": "数据分析师，可以查看和分析所有数据",
        "level": 2,
        "is_default": False,
        "is_system": True
    },
    {
        "name": "高级用户",
        "code": "premium",
        "description": "高级用户，可以查看所有情报和高级功能",
        "level": 3,
        "is_default": False,
        "is_system": False
    },
    {
        "name": "普通用户",
        "code": "normal",
        "description": "普通用户，只能查看基本情报",
        "level": 4,
        "is_default": True,
        "is_system": False
    }
]

SYSTEM_PERMISSIONS = [
    # 用户管理权限
    {"name": "查看用户列表", "code": "user.read", "resource": "user", "action": "read"},
    {"name": "创建用户", "code": "user.create", "resource": "user", "action": "create"},
    {"name": "编辑用户", "code": "user.update", "resource": "user", "action": "update"},
    {"name": "删除用户", "code": "user.delete", "resource": "user", "action": "delete"},
    
    # 角色管理权限
    {"name": "查看角色列表", "code": "role.read", "resource": "role", "action": "read"},
    {"name": "创建角色", "code": "role.create", "resource": "role", "action": "create"},
    {"name": "编辑角色", "code": "role.update", "resource": "role", "action": "update"},
    {"name": "删除角色", "code": "role.delete", "resource": "role", "action": "delete"},
    
    # 权限管理权限
    {"name": "查看权限列表", "code": "permission.read", "resource": "permission", "action": "read"},
    {"name": "创建权限", "code": "permission.create", "resource": "permission", "action": "create"},
    {"name": "编辑权限", "code": "permission.update", "resource": "permission", "action": "update"},
    {"name": "删除权限", "code": "permission.delete", "resource": "permission", "action": "delete"},
    
    # 比赛管理权限
    {"name": "查看比赛列表", "code": "match.read", "resource": "match", "action": "read"},
    {"name": "查看比赛详情", "code": "match.read_detail", "resource": "match", "action": "read_detail"},
    {"name": "创建比赛", "code": "match.create", "resource": "match", "action": "create"},
    {"name": "编辑比赛", "code": "match.update", "resource": "match", "action": "update"},
    {"name": "删除比赛", "code": "match.delete", "resource": "match", "action": "delete"},
    
    # 情报管理权限
    {"name": "查看情报列表", "code": "intelligence.read", "resource": "intelligence", "action": "read"},
    {"name": "查看情报详情", "code": "intelligence.read_detail", "resource": "intelligence", "action": "read_detail"},
    {"name": "创建情报", "code": "intelligence.create", "resource": "intelligence", "action": "create"},
    {"name": "编辑情报", "code": "intelligence.update", "resource": "intelligence", "action": "update"},
    {"name": "删除情报", "code": "intelligence.delete", "resource": "intelligence", "action": "delete"},
    
    # 高级数据权限
    {"name": "查看赔率数据", "code": "odds.read", "resource": "odds", "action": "read"},
    {"name": "查看高级统计", "code": "stats.advanced", "resource": "stats", "action": "advanced"},
    {"name": "查看预测数据", "code": "prediction.read", "resource": "prediction", "action": "read"},
    
    # 系统管理权限
    {"name": "访问管理后台", "code": "admin.access", "resource": "admin", "action": "access"},
    {"name": "查看系统日志", "code": "log.read", "resource": "log", "action": "read"},
    {"name": "管理系统配置", "code": "config.manage", "resource": "config", "action": "manage"},
    {"name": "查看系统状态", "code": "system.status", "resource": "system", "action": "status"},
    
    # 数据导入导出权限
    {"name": "导入数据", "code": "data.import", "resource": "data", "action": "import"},
    {"name": "导出数据", "code": "data.export", "resource": "data", "action": "export"},
]