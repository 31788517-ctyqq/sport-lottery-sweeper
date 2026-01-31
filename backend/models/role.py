from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.core.database import Base
from backend.core.base_model import BaseFullModel
from backend.models.admin_user import AdminUser


class Role(BaseFullModel):
    """角色模型"""
    __tablename__ = "roles"

    # 基本信息
    name = Column(String(100), nullable=False, index=True, unique=True)  # 角色名称
    description = Column(Text, nullable=True)  # 角色描述
    permissions = Column(Text, nullable=True)  # 权限列表（JSON格式存储）
    status = Column(Boolean, default=True, nullable=False, index=True)  # 状态
    sort_order = Column(Integer, default=0, nullable=False)  # 排序

    # 外键关联
    # AI_WORKING: coder1 @2026-01-28 - 注释掉无效的relationship，因为AdminUser使用枚举角色而非外键关联
    # admin_users = relationship("AdminUser", back_populates="role")
    # AI_DONE: coder1 @2026-01-28

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}')>"