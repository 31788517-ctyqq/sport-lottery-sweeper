"""
爬虫配置数据模型
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, ForeignKey
)
from sqlalchemy.orm import relationship

from .base import BaseAuditModel


class CrawlerConfig(BaseAuditModel):
    """
    爬虫配置模型
    用于存储爬虫相关的配置参数
    """
    __tablename__ = "crawler_configs"
    __table_args__ = {'extend_existing': True}
    
    # 爬虫基本信息
    name = Column(String(200), nullable=False, index=True, unique=True)
    description = Column(Text, nullable=True)
    
    # 爬虫配置
    url = Column(String(500), nullable=False)
    frequency = Column(Integer, nullable=False, default=3600)  # 爬取频率（秒）
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # 配置详情（JSON格式）
    config_data = Column(Text, nullable=False)
    
    # 关联信息
    created_by = Column(Integer, ForeignKey('admin_users.id', ondelete='SET NULL'), nullable=True, index=True)
    updated_by = Column(Integer, ForeignKey('admin_users.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # 关系
    creator = relationship("AdminUser", foreign_keys=[created_by])
    updater = relationship("AdminUser", foreign_keys=[updated_by])