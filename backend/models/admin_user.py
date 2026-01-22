"""
后台管理用户数据模型
用于管理具有后台权限的运营人员/管理员
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from sqlalchemy.ext.mutable import MutableDict
from .base import Base, BaseAuditModel


class AdminRoleEnum(enum.Enum):
    """后台用户角色枚举"""
    SUPER_ADMIN = "super_admin"      # 超级管理员 - 所有权限
    ADMIN = "admin"                  # 管理员 - 大部分管理权限
    MODERATOR = "moderator"          # 内容审核员 - 内容审核权限
    AUDITOR = "auditor"              # 审计员 - 查看日志和报表
    OPERATOR = "operator"            # 运营人员 - 数据录入和维护


class AdminStatusEnum(enum.Enum):
    """后台用户状态枚举"""
    ACTIVE = "active"                # 激活
    INACTIVE = "inactive"            # 未激活
    SUSPENDED = "suspended"          # 暂停
    LOCKED = "locked"                # 锁定


class AdminUser(BaseAuditModel):
    """
    后台管理用户模型
    用于管理具有后台权限的运营人员和管理员
    """
    __tablename__ = "admin_users"
    __table_args__ = {'extend_existing': True}
    
    # 基本信息
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # 个人信息
    real_name = Column(String(100), nullable=False, index=True)  # 真实姓名（必填）
    phone = Column(String(20), nullable=True, index=True)
    department = Column(String(100), nullable=True, index=True)  # 所属部门
    position = Column(String(100), nullable=True)  # 职位
    
    # 角色和权限
    role = Column(Enum(AdminRoleEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), default=AdminRoleEnum.OPERATOR, nullable=False, index=True)
    status = Column(Enum(AdminStatusEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), default=AdminStatusEnum.INACTIVE, nullable=False, index=True)
    
    # 安全设置
    two_factor_enabled = Column(Boolean, default=False, nullable=False)  # 是否启用双因素认证
    two_factor_secret = Column(String(32), nullable=True)  # 双因素认证密钥
    login_allowed_ips = Column(Text, nullable=True)  # 存储为JSON数组字符串
    password_expires_at = Column(DateTime(timezone=True), nullable=True)  # 密码过期时间
    must_change_password = Column(Boolean, default=True, nullable=False)  # 首次登录必须修改密码
    
    # 账户状态
    is_verified = Column(Boolean, default=False, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)  # 失败登录次数
    last_failed_login_at = Column(DateTime(timezone=True), nullable=True)  # 最后失败登录时间
    locked_until = Column(DateTime(timezone=True), nullable=True)  # 锁定截止时间
    
    # 登录信息
    last_login_at = Column(DateTime(timezone=True), nullable=True, index=True)
    last_login_ip = Column(String(45), nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    
    # 创建和管理信息
    created_by = Column(Integer, ForeignKey('admin_users.id', ondelete='SET NULL'), nullable=True, index=True)
    remarks = Column(Text, nullable=True)  # 备注
    
    # 偏好设置
    preferences = Column(Text, default='{}', nullable=False)  # 个人偏好设置
    
    # 关系
    operation_logs = relationship("AdminOperationLog", back_populates="admin_user", cascade="all, delete-orphan")
    login_logs = relationship("AdminLoginLog", back_populates="admin_user", cascade="all, delete-orphan")
    creator = relationship("AdminUser", remote_side="AdminUser.id", backref="created_admins")


class AdminOperationLog(Base):
    """
    后台操作日志模型
    记录所有后台用户的操作行为
    """
    __tablename__ = "admin_operation_logs"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey('admin_users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # 操作信息
    action = Column(String(50), nullable=False, index=True)  # create, update, delete, export, etc.
    resource_type = Column(String(50), nullable=False, index=True)  # user, match, intelligence, etc.
    resource_id = Column(String(50), nullable=True, index=True)  # 资源ID
    resource_name = Column(String(255), nullable=True)  # 资源名称
    
    # 请求信息
    method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE
    path = Column(String(500), nullable=False)  # 请求路径
    query_params = Column(MutableDict.as_mutable(Text), default=lambda: {}, nullable=False)  # 查询参数
    request_body = Column(MutableDict.as_mutable(Text), nullable=True)  # 请求体（敏感信息需过滤）
    
    # 响应信息
    status_code = Column(Integer, nullable=False, index=True)  # HTTP状态码
    response_data = Column(MutableDict.as_mutable(Text), nullable=True)  # 响应数据（敏感信息需过滤）
    
    # 环境信息
    ip_address = Column(String(45), nullable=False, index=True)
    user_agent = Column(Text, nullable=True)
    
    # 变更信息（用于审计）
    changes_before = Column(MutableDict.as_mutable(Text), nullable=True)  # 变更前的数据
    changes_after = Column(MutableDict.as_mutable(Text), nullable=True)   # 变更后的数据
    
    # 时间信息
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    duration_ms = Column(Integer, nullable=True)  # 操作耗时（毫秒）
    
    # 关系
    admin_user = relationship("AdminUser", back_populates="operation_logs")


class AdminLoginLog(Base):
    """
    后台用户登录日志模型
    """
    __tablename__ = "admin_login_logs"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey('admin_users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # 登录信息
    login_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    login_ip = Column(String(45), nullable=False, index=True)
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, default=True, nullable=False, index=True)
    failure_reason = Column(String(255), nullable=True)  # 失败原因
    
    # 地理位置信息
    country = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    
    # 设备信息
    device_type = Column(String(50), nullable=True)  # desktop, mobile, tablet
    os = Column(String(50), nullable=True)
    browser = Column(String(50), nullable=True)
    
    # 安全信息
    two_factor_used = Column(Boolean, default=False, nullable=False)  # 是否使用了双因素认证
    ip_whitelisted = Column(Boolean, default=False, nullable=False)   # IP是否在白名单中
    
    # 关系
    admin_user = relationship("AdminUser", back_populates="login_logs")


# 系统后台角色权限配置
ADMIN_ROLE_PERMISSIONS = {
    "super_admin": {
        "name": "超级管理员",
        "description": "拥有所有系统权限",
        "permissions": ["*"]  # 所有权限
    },
    "admin": {
        "name": "管理员",
        "description": "拥有大部分管理权限，除了系统配置和超管管理",
        "permissions": [
            "user.*", "match.*", "intelligence.*", "odds.*",
            "admin.view", "admin.user.manage", "log.read"
        ]
    },
    "moderator": {
        "name": "内容审核员",
        "description": "负责内容审核和管理",
        "permissions": [
            "user.read", "user.update.status",
            "match.read", "match.update", "match.delete",
            "intelligence.read", "intelligence.update", "intelligence.delete",
            "admin.view"
        ]
    },
    "auditor": {
        "name": "审计员",
        "description": "查看所有数据和日志，但不能修改",
        "permissions": [
            "user.read", "match.read", "intelligence.read", "odds.read",
            "admin.view", "log.read", "report.view"
        ]
    },
    "operator": {
        "name": "运营人员",
        "description": "负责日常数据录入和维护",
        "permissions": [
            "match.read", "match.create", "match.update",
            "intelligence.read", "intelligence.create", "intelligence.update",
            "admin.view"
        ]
    }
}
