"""
系统配置数据模型
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, ForeignKey
)
from sqlalchemy.orm import relationship

from .base import BaseAuditModel


class SystemConfig(BaseAuditModel):
    """
    系统配置模型
    用于存储系统级别的配置参数
    """
    __tablename__ = "system_configs"
    __table_args__ = {'extend_existing': True}
    
    # 配置基本信息
    config_key = Column(String(200), nullable=False, index=True, unique=True)
    config_name = Column(String(200), nullable=False, index=True)
    
    # 配置值
    config_value = Column(Text, nullable=False)
    config_type = Column(String(50), nullable=False, default="string", index=True)  # string, integer, boolean, json
    
    # 描述和分组
    description = Column(Text, nullable=True)
    group = Column(String(100), nullable=True, index=True)  # 配置分组
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # 关联信息
    created_by = Column(Integer, ForeignKey('admin_users.id', ondelete='SET NULL'), nullable=True, index=True)
    updated_by = Column(Integer, ForeignKey('admin_users.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # 关系
    creator = relationship("AdminUser", foreign_keys=[created_by])
    updater = relationship("AdminUser", foreign_keys=[updated_by])