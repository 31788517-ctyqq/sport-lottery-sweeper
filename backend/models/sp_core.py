"""
足球SP管理模块 - 核心SP值管理
仅包含SP值相关的核心功能，删除比赛信息管理模块以解决数据冲突
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey, Index
from .base import Base
from sqlalchemy.orm import relationship
from datetime import datetime
import json
import uuid

# 从data_sources模块导入DataSource，避免重复定义
from .data_sources import DataSource

# 导入OddsCompany模型而不是重新定义
from .odds_companies import OddsCompany


class SPRecord(Base):
    """SP值记录表 - 核心SP值管理"""
    
    __tablename__ = 'sp_records'
    __table_args__ = {'extend_existing': True}  # 解决表重复定义问题
    
    id = Column(Integer, primary_key=True, index=True)
    # 关联到现有的matches表，但不管理比赛信息
    match_identifier = Column(String(50), nullable=False, comment="比赛标识符（引用现有matches表）")
    company_id = Column(Integer, ForeignKey('odds_companies.id'), nullable=False, comment="赔率公司ID")
    data_source_id = Column(Integer, ForeignKey('data_sources.id'), nullable=False, comment="数据源ID")
    
    # SP值核心字段
    handicap_type = Column(String(20), nullable=False, default='handicap', comment="盘口类型")
    handicap_value = Column(Float, comment="让球数值")
    sp_value = Column(Float, nullable=False, comment="SP值")
    implied_probability = Column(Float, comment="隐含概率")
    
    # 元数据
    recorded_at = Column(DateTime, nullable=False, comment="记录时间")
    raw_data = Column(JSON, comment="原始数据快照")
    confidence_level = Column(Float, default=1.0, comment="置信度")
    is_valid = Column(Boolean, default=True, comment="数据有效性")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    company = relationship("OddsCompany", back_populates="sp_records")
    data_source = relationship("DataSource", back_populates="sp_records")
    modifications = relationship("SPModificationLog", back_populates="sp_record")
    
    def to_dict(self):
        return {
            'id': self.id,
            'match_identifier': self.match_identifier,
            'company_id': self.company_id,
            'company_name': self.company.company_name if self.company else None,
            'data_source_id': self.data_source_id,
            'handicap_type': self.handicap_type,
            'handicap_value': self.handicap_value,
            'sp_value': self.sp_value,
            'implied_probability': self.implied_probability,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'confidence_level': self.confidence_level,
            'is_valid': self.is_valid,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SPModificationLog(Base):
    """SP值修改日志表"""
    
    __tablename__ = 'sp_modification_logs'
    __table_args__ = {'extend_existing': True}  # 解决表重复定义问题
    
    id = Column(Integer, primary_key=True, index=True)
    sp_record_id = Column(Integer, ForeignKey('sp_records.id'), nullable=False)
    modified_by = Column(Integer, comment="修改人ID")
    old_value = Column(Float, nullable=False, comment="原值")
    new_value = Column(Float, nullable=False, comment="新值")
    old_handicap = Column(Float, comment="原让球值")
    new_handicap = Column(Float, comment="新让球值")
    reason = Column(String(200), comment="修改原因")
    ip_address = Column(String(45), comment="IP地址")
    user_agent = Column(Text, comment="用户代理")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    sp_record = relationship("SPRecord", back_populates="modifications")
    
    def to_dict(self):
        return {
            'id': self.id,
            'sp_record_id': self.sp_record_id,
            'modified_by': self.modified_by,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'old_handicap': self.old_handicap,
            'new_handicap': self.new_handicap,
            'reason': self.reason,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# 创建索引以提高查询性能
Index('idx_sp_match_company', SPRecord.match_identifier, SPRecord.company_id)
Index('idx_sp_recorded_time', SPRecord.recorded_at)
Index('idx_sp_company_time', SPRecord.company_id, SPRecord.recorded_at)
Index('idx_sp_match_time', SPRecord.match_identifier, SPRecord.recorded_at)

# 为DataSource添加反向关系，这样SPRecord才能正确关联回去
if not hasattr(DataSource, 'sp_records'):
    # 动态添加关系
    DataSource.sp_records = relationship("SPRecord", back_populates="data_source")

# 预定义常量
HANDICAP_TYPES = {
    'handicap': '让球盘',
    'no_handicap': '不让球',
    'over_under': '大小球',
    'corner': '角球',
    'yellow_card': '黄牌'
}

DATA_SOURCE_TYPES = {
    'api': 'API接口',
    'file': '本地文件',
    'manual': '手动录入'
}

MODIFICATION_REASONS = {
    'correction': '数据纠错',
    'adjustment': '市场调整',
    'manual_entry': '手动补录',
    'system_error': '系统错误修正'
}