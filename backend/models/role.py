from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.models.base import Base, BaseFullModel
from backend.models.admin_user import AdminUser
import enum


class RoleLevelEnum(enum.Enum):
    """角色等级枚举"""
    SUPER_ADMIN = 5      # 超级管理员 - 所有权限
    ADMIN = 4            # 管理员 - 大部分管理权限
    AUDITOR = 3          # 审计员 - 查看日志和报表
    OPERATOR = 2         # 运营员 - 数据维护和执行权限
    OBSERVER = 1         # 观察者 - 只读访问


class Role(BaseFullModel):
    """角色模型"""
    __tablename__ = "roles"

    # 基本信息
    name = Column(String(100), nullable=False, index=True, unique=True)  # 角色名称
    description = Column(Text, nullable=True)  # 角色描述
    permissions = Column(Text, nullable=True)  # 权限列表（JSON格式存储）
    level = Column(Integer, nullable=False, default=1, index=True)  # 角色级别 (1-5)
    is_system = Column(Boolean, default=False, nullable=False)  # 是否为系统内置角色
    status = Column(Boolean, default=True, nullable=False, index=True)  # 状态
    sort_order = Column(Integer, default=0, nullable=False)  # 排序

    # 外键关联
    # AI_WORKING: coder1 @2026-01-28 - 注释掉无效的relationship，因为AdminUser使用枚举角色而非外键关联
    # admin_users = relationship("AdminUser", back_populates="role")
    # AI_DONE: coder1 @2026-01-28

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}')>"