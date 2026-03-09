"""
管理数据模型
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, JSON
)
from sqlalchemy.orm import relationship
import enum

from sqlalchemy.ext.mutable import MutableDict
from .base import BaseAuditModel


class DataCategoryEnum(enum.Enum):
    """数据分类枚举"""
    SYSTEM_CONFIG = "system_config"      # 系统配置
    CRAWLER_CONFIG = "crawler_config"    # 爬虫配置
    INTELLIGENCE_RECORD = "intelligence_record"  # 情报记录
    MATCH_DATA = "match_data"           # 比赛数据
    USER_DATA = "user_data"             # 用户数据
    OTHER = "other"                     # 其他


class AdminData(BaseAuditModel):
    """
    管理数据模型
    用于存储各种管理相关的数据
    """
    __tablename__ = "admin_data"
    __table_args__ = {'extend_existing': True}
    
    # 基本信息
    name = Column(String(200), nullable=False, index=True)
    category = Column(Enum(DataCategoryEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), default=DataCategoryEnum.OTHER, nullable=False, index=True)
    key = Column(String(200), nullable=False, index=True, unique=True)
    
    # 数据内容
    value = Column(MutableDict.as_mutable(Text), nullable=False)
    description = Column(Text, nullable=True)
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # 关联信息
    created_by = Column(Integer, ForeignKey('admin_users.id', ondelete='SET NULL'), nullable=True, index=True)
    updated_by = Column(Integer, ForeignKey('admin_users.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # 关系
    creator = relationship("AdminUser", foreign_keys=[created_by])
    updater = relationship("AdminUser", foreign_keys=[updated_by])