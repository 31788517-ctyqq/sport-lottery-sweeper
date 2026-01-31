"""
数据审核数据模型
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, 
    ForeignKey, Float, Text, Enum, CheckConstraint, Index, JSON
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
import enum

from sqlalchemy.ext.mutable import MutableDict
from .base import Base, BaseAuditModel, BaseFullModel


class DataTypeEnum(enum.Enum):
    """数据类型枚举"""
    MATCH = "match"                         # 比赛数据
    INTELLIGENCE = "intelligence"           # 情报数据
    ODDS = "odds"                          # 赔率数据
    PREDICTION = "prediction"              # 预测数据
    USER_DATA = "user_data"                # 用户数据
    TEAM = "team"                          # 球队数据
    LEAGUE = "league"                      # 联赛数据
    VENUE = "venue"                        # 场馆数据


class ReviewStatusEnum(enum.Enum):
    """审核状态枚举"""
    PENDING = "pending"                     # 待审核
    APPROVED = "approved"                   # 已批准
    REJECTED = "rejected"                   # 已拒绝
    NEEDS_MORE_INFO = "needs_more_info"    # 需要更多信息
    UNDER_REVIEW = "under_review"          # 审核中


class DataReview(BaseFullModel):
    """
    数据审核模型
    """
    __tablename__ = "data_reviews"
    __table_args__ = {'extend_existing': True}  # 添加此选项以允许扩展已存在的表
    
    # 数据信息
    data_type = Column(Enum(DataTypeEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), nullable=False, index=True)  # 数据类型
    data_id = Column(Integer, nullable=False, index=True)  # 数据ID
    data_table = Column(String(100), nullable=False, index=True)  # 数据表名
    
    # 数据快照
    data_snapshot = Column(MutableDict.as_mutable(Text), default=lambda: {}, nullable=False)  # 审核时的数据快照
    
    # 审核状态
    review_status = Column(Enum(ReviewStatusEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), default=ReviewStatusEnum.PENDING, nullable=False, index=True)
    reviewer_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)  # 审核人
    
    # 审核信息
    review_notes = Column(Text, nullable=True)  # 审核备注
    reviewed_at = Column(DateTime(timezone=True), nullable=True, index=True)  # 审核时间
    
    # 审核原因
    approval_reason = Column(Text, nullable=True)  # 批准原因
    rejection_reason = Column(Text, nullable=True)  # 拒绝原因
    
    # 外部验证
    external_validation_source = Column(String(200), nullable=True)  # 外部验证源
    validation_result = Column(MutableDict.as_mutable(Text), default=lambda: {}, nullable=False)  # 验证结果
    
    # 优先级
    priority = Column(Integer, default=0, nullable=False, index=True)  # 优先级
    
    # 自动审核标记
    is_auto_approved = Column(Boolean, default=False, nullable=False, index=True)  # 是否自动批准
    auto_approval_reason = Column(String(200), nullable=True)  # 自动批准原因
    
    # 验证分数
    validation_score = Column(Float, default=0.0, nullable=False, index=True)  # 验证分数 (0-1)
    
    # 重新审核
    requires_resubmission = Column(Boolean, default=False, nullable=False, index=True)  # 是否需要重新提交
    resubmission_deadline = Column(DateTime(timezone=True), nullable=True)  # 重新提交截止时间
    
    # 关系 - 暂时移除对User的直接引用
    # reviewer = relationship("User")
    
    # 索引
    __table_args__ = (
        Index('idx_data_reviews_type_status', 'data_type', 'review_status'),
        Index('idx_data_reviews_status_reviewer', 'review_status', 'reviewer_id'),
        Index('idx_data_reviews_priority_status', 'priority', 'review_status'),
        Index('idx_data_reviews_data_type_id', 'data_type', 'data_id'),
        Index('idx_data_reviews_table_status', 'data_table', 'review_status'),
        Index('idx_data_reviews_valid_score', 'validation_score'),
        Index('idx_data_reviews_requires_resubmit', 'requires_resubmission'),
        {'extend_existing': True}  # 确保支持表扩展
    )


class ValidationRule(BaseFullModel):
    """
    验证规则模型
    """
    __tablename__ = "validation_rules"
    __table_args__ = {'extend_existing': True}  # 添加此选项以允许扩展已存在的表
    
    # 规则信息
    name = Column(String(100), nullable=False, index=True)  # 规则名称
    code = Column(String(50), unique=True, nullable=False, index=True)  # 规则代码
    description = Column(Text, nullable=True)  # 规则描述
    
    # 应用范围
    applies_to = Column(Enum(DataTypeEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), nullable=False, index=True)  # 应用于哪种数据类型
    severity = Column(String(20), default='medium', nullable=False, index=True)  # 严重程度 (low, medium, high, critical)
    
    # 规则条件
    condition_expression = Column(Text, nullable=False)  # 规则条件表达式
    error_message = Column(String(500), nullable=False)  # 错误消息
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # 自动执行
    auto_execute = Column(Boolean, default=True, nullable=False)  # 是否自动执行
    auto_approve_if_pass = Column(Boolean, default=False, nullable=False)  # 通过时是否自动批准
    
    # 配置
    config = Column(MutableDict.as_mutable(Text), default=lambda: {}, nullable=False)  # 规则配置
    
    # 索引
    __table_args__ = (
        Index('idx_validation_rules_active', 'is_active'),
        Index('idx_validation_rules_applies_severity', 'applies_to', 'severity'),
        Index('idx_validation_rules_auto_exec', 'auto_execute'),
        {'extend_existing': True}  # 确保支持表扩展
    )


class ValidationError(BaseFullModel):
    """
    验证错误模型
    """
    __tablename__ = "validation_errors"
    __table_args__ = {'extend_existing': True}  # 添加此选项以允许扩展已存在的表
    
    # 关联信息
    review_id = Column(Integer, ForeignKey('data_reviews.id', ondelete='CASCADE'), nullable=False, index=True)
    rule_id = Column(Integer, ForeignKey('validation_rules.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # 错误信息
    error_code = Column(String(50), nullable=False, index=True)  # 错误代码
    error_message = Column(Text, nullable=False)  # 错误消息
    severity = Column(String(20), nullable=False, index=True)  # 严重程度
    
    # 字段信息
    field_name = Column(String(100), nullable=True, index=True)  # 出错字段名
    field_value = Column(Text, nullable=True)  # 出错字段值
    
    # 状态
    resolved = Column(Boolean, default=False, nullable=False, index=True)  # 是否已解决
    resolved_at = Column(DateTime(timezone=True), nullable=True)  # 解决时间
    resolved_by_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)  # 解决人ID
    
    # 关系 - 暂时移除对User的直接引用
    # review = relationship("DataReview")
    # rule = relationship("ValidationRule")
    # resolver = relationship("User", foreign_keys=[resolved_by])
    
    # 索引
    __table_args__ = (
        Index('idx_validation_errors_review_resolved', 'review_id', 'resolved'),
        Index('idx_validation_errors_rule_severity', 'rule_id', 'severity'),
        Index('idx_validation_errors_field_resolved', 'field_name', 'resolved'),
        Index('idx_validation_errors_error_code', 'error_code'),
        {'extend_existing': True}  # 确保支持表扩展
    )


# 修复关系映射问题
def _setup_relationships():
    """
    设置模型间的关系，解决循环导入问题
    """
    from sqlalchemy import event
    from sqlalchemy.orm import mapper
    from .user import User

    @event.listens_for(mapper, 'after_configured', once=True)
    def setup_data_review_relationships():
        """在所有模型配置完成后设置关系"""
        # 为DataReview模型添加到User的关系
        DataReview.reviewer = relationship(
            "User", 
            foreign_keys=[DataReview.reviewer_id],
            lazy='select'
        )
        
        # 为ValidationError模型添加关系
        ValidationError.review = relationship("DataReview")
        ValidationError.rule = relationship("ValidationRule")
        ValidationError.resolver = relationship(
            "User",
            foreign_keys=[ValidationError.resolved_by_id],
            lazy='select'
        )


# 设置关系
_setup_relationships()