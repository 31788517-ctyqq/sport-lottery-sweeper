"""
智能分析记录数据模型
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, ForeignKey
)
from sqlalchemy.orm import relationship

from .base import BaseAuditModel


class IntelligenceRecord(BaseAuditModel):
    """
    智能分析记录模型
    用于存储AI智能分析的结果记录
    """
    __tablename__ = "intelligence_records"
    __table_args__ = {'extend_existing': True}
    
    # 分析基本信息
    analysis_type = Column(String(100), nullable=False, index=True)
    title = Column(String(200), nullable=False, index=True)
    
    # 分析内容
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    
    # 关联信息
    match_id = Column(Integer, ForeignKey('matches.id', ondelete='CASCADE'), nullable=True, index=True)
    team_id = Column(Integer, ForeignKey('teams.id', ondelete='CASCADE'), nullable=True, index=True)
    league_id = Column(Integer, ForeignKey('leagues.id', ondelete='CASCADE'), nullable=True, index=True)
    
    # 分析元数据
    confidence_score = Column(Integer, nullable=True)  # 置信度分数 (0-100)
    is_verified = Column(Boolean, default=False, nullable=False, index=True)
    
    # 关联信息
    created_by = Column(Integer, ForeignKey('admin_users.id', ondelete='SET NULL'), nullable=True, index=True)
    verified_by = Column(Integer, ForeignKey('admin_users.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # 关系
    creator = relationship("AdminUser", foreign_keys=[created_by])
    verifier = relationship("AdminUser", foreign_keys=[verified_by])
    match = relationship("Match")
    team = relationship("Team")
    league = relationship("League")