"""
情报数据模型
"""
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, 
    ForeignKey, Float, Text, Enum, CheckConstraint, Index, Date, JSON
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
import enum

from sqlalchemy.ext.mutable import MutableDict
from .base import Base, BaseAuditModel, BaseFullModel

# 情报类型枚举
class IntelligenceTypeEnum(enum.Enum):
    """情报类型枚举"""
    INJURY = "injury"                    # 伤病信息
    SUSPENSION = "suspension"            # 停赛信息
    LINEUP = "lineup"                    # 阵容信息
    TACTICS = "tactics"                  # 战术分析
    WEATHER = "weather"                  # 天气信息
    REFEREE = "referee"                  # 裁判信息
    VENUE = "venue"                      # 场地信息
    ODDS = "odds"                        # 赔率信息
    TRANSFER = "transfer"                # 转会信息
    RUMOR = "rumor"                      # 传闻信息
    PREDICTION = "prediction"            # 预测分析
    STATISTICS = "statistics"            # 统计数据
    PREVIEW = "preview"                  # 赛前预告
    REVIEW = "review"                    # 赛后回顾
    MOTIVATION = "motivation"            # 战意分析
    HISTORY = "history"                  # 历史交锋
    FORM = "form"                        # 近期状态
    OTHER = "other"                      # 其他信息

# 情报来源枚举
class IntelligenceSourceEnum(enum.Enum):
    """情报来源枚举"""
    OFFICIAL = "official"                # 官方渠道
    BOOKMAKER = "bookmaker"              # 博彩公司
    MEDIA = "media"                      # 媒体
    SOCIAL_MEDIA = "social_media"        # 社交媒体
    EXPERT = "expert"                    # 专家分析
    AI_ANALYSIS = "ai_analysis"          # AI分析
    USER_SUBMISSION = "user_submission"  # 用户提交
    SYSTEM = "system"                    # 系统生成

# 情报置信度枚举
class ConfidenceLevelEnum(enum.Enum):
    """情报置信度枚举"""
    VERY_LOW = "very_low"        # 非常低 (0-20%)
    LOW = "low"                  # 低 (21-40%)
    MEDIUM = "medium"            # 中等 (41-60%)
    HIGH = "high"                # 高 (61-80%)
    VERY_HIGH = "very_high"      # 非常高 (81-100%)
    CONFIRMED = "confirmed"      # 已确认 (100%)

# 情报重要性枚举
class ImportanceLevelEnum(enum.Enum):
    """情报重要性枚举"""
    LOW = "low"                  # 低重要性
    MEDIUM = "medium"            # 中重要性
    HIGH = "high"                # 高重要性
    CRITICAL = "critical"        # 关键重要性

class IntelligenceType(Base):
    """
    情报类型模型
    """
    __tablename__ = "intelligence_types"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 基本信息
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)  # 图标名称
    
    # 分类信息
    category = Column(String(50), nullable=False, index=True)  # team, player, match, odds, etc.
    subcategory = Column(String(50), nullable=True)
    
    # 属性
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_system = Column(Boolean, default=False, nullable=False)  # 是否为系统类型
    default_weight = Column(Float, default=0.5, nullable=False)  # 默认权重
    default_confidence = Column(Enum(ConfidenceLevelEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), default=ConfidenceLevelEnum.MEDIUM, nullable=False)
    
    # 显示设置
    display_order = Column(Integer, default=0, nullable=False)
    color = Column(String(20), nullable=True)  # 显示颜色
    
    # 关系
    intelligence_items = relationship("Intelligence", back_populates="type_info", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_intel_types_active_category', 'is_active', 'category'),
        Index('idx_intel_types_system', 'is_system'),
        Index('idx_intel_types_code', 'code'),
    )
    
    def __repr__(self) -> str:
        return f"<IntelligenceType(id={self.id}, name={self.name}, code={self.code})>"

class IntelligenceSource(Base):
    """
    信息来源模型
    """
    __tablename__ = "intelligence_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 基本信息
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # 来源属性
    source_type = Column(String(50), nullable=False, index=True)  # website, api, social_media, etc.
    url = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)
    
    # 可信度设置
    reliability_score = Column(Float, default=0.5, nullable=False)  # 可信度评分 (0-1)
    update_frequency = Column(String(50), nullable=True)  # 更新频率
    is_verified = Column(Boolean, default=False, nullable=False, index=True)
    is_official = Column(Boolean, default=False, nullable=False, index=True)
    
    # 状态信息
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_crawled_at = Column(DateTime(timezone=True), nullable=True)
    
    # 配置信息
    config = Column(MutableDict.as_mutable(Text), default=lambda: {}, nullable=False)  # 抓取配置
    
    # 统计信息
    total_items = Column(Integer, default=0, nullable=False)
    success_rate = Column(Float, default=0.0, nullable=False)
    
    # 关系
    intelligence_items = relationship("Intelligence", back_populates="source_info", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_intel_sources_active_reliable', 'is_active', 'is_verified'),
        Index('idx_intel_sources_type', 'source_type'),
        Index('idx_intel_sources_code', 'code'),
        CheckConstraint('reliability_score >= 0.0 AND reliability_score <= 1.0', name='ck_reliability_score_range'),
        CheckConstraint('success_rate >= 0.0 AND success_rate <= 1.0', name='ck_success_rate_range')
    )
    
    def __repr__(self) -> str:
        return f"<IntelligenceSource(id={self.id}, name={self.name}, code={self.code})>"

class Intelligence(BaseFullModel):
    """
    情报数据模型
    """
    __tablename__ = "intelligence"
    
    # 关联信息 - 使用外键ID而非code，提高查询效率
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="SET NULL"), nullable=True, index=True)
    type_id = Column(Integer, ForeignKey("intelligence_types.id", ondelete="SET NULL"), nullable=True, index=True)
    source_id = Column(Integer, ForeignKey("intelligence_sources.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # 内容信息
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)  # AI生成的摘要
    keywords = Column(Text, default='[]', nullable=False)  # 存储为JSON数组字符串
    tags = Column(Text, default='[]', nullable=False)  # 存储为JSON数组字符串
    
    # 置信度和重要性
    confidence = Column(Enum(ConfidenceLevelEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), default=ConfidenceLevelEnum.MEDIUM, nullable=False, index=True)
    confidence_score = Column(Float, default=0.5, nullable=False)  # 数值化的置信度 (0-1)
    importance = Column(Enum(ImportanceLevelEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), default=ImportanceLevelEnum.MEDIUM, nullable=False, index=True)
    
    # 权重计算
    base_weight = Column(Float, default=0.5, nullable=False)  # 基础权重
    weight_multiplier = Column(Float, default=1.0, nullable=False)  # 权重乘数
    calculated_weight = Column(Float, default=0.0, nullable=False, index=True)  # 计算后的最终权重
    
    # 时间信息
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)  # 原始发布时间
    event_time = Column(DateTime(timezone=True), nullable=True, index=True)  # 事件发生时间
    expiration_at = Column(DateTime(timezone=True), nullable=True, index=True)  # 信息过期时间
    
    # 状态信息
    status = Column(String(50), default="active", nullable=False, index=True)  # active, verified, outdated, deleted
    is_verified = Column(Boolean, default=False, nullable=False, index=True)
    is_duplicate = Column(Boolean, default=False, nullable=False, index=True)
    duplicate_of = Column(Integer, ForeignKey("intelligence.id", ondelete="SET NULL"), nullable=True)  # 重复情报的ID
    
    # 审核信息
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True, index=True)
    review_notes = Column(Text, nullable=True)
    
    # 外部数据
    external_id = Column(String(100), nullable=True, index=True)  # 外部系统ID
    external_url = Column(String(500), nullable=True)  # 原始信息来源URL
    external_data = Column(MutableDict.as_mutable(Text), default=lambda: {}, nullable=False)  # 原始数据
    
    # 关联数据
    odds_data = Column(MutableDict.as_mutable(Text), default=lambda: {}, nullable=False)  # 赔率数据
    stats_data = Column(MutableDict.as_mutable(Text), default=lambda: {}, nullable=False)  # 统计数据
    prediction_data = Column(MutableDict.as_mutable(Text), default=lambda: {}, nullable=False)  # 预测数据
    
    # 附件信息
    attachments = Column(MutableDict.as_mutable(Text), default=lambda: {}, nullable=False)  # 附件信息
    images = Column(Text, default='[]', nullable=False)  # 存储为JSON数组字符串
    
    # 统计信息
    view_count = Column(Integer, default=0, nullable=False, index=True)
    like_count = Column(Integer, default=0, nullable=False, index=True)
    comment_count = Column(Integer, default=0, nullable=False, index=True)
    share_count = Column(Integer, default=0, nullable=False, index=True)
    
    # 热门度
    popularity_score = Column(Float, default=0.0, nullable=False, index=True)
    trending_score = Column(Float, default=0.0, nullable=False, index=True)  # 趋势得分
    
    # 关系 - 延迟导入避免循环依赖
    match = relationship("Match", back_populates="intelligence_items", overlaps="intelligence")
    team = relationship("Team", back_populates="intelligence_items")
    player = relationship("Player", back_populates="intelligence_items")
    type_info = relationship("IntelligenceType", back_populates="intelligence_items")
    source_info = relationship("IntelligenceSource", back_populates="intelligence_items")
    related_intelligence = relationship("IntelligenceRelation", foreign_keys="IntelligenceRelation.intelligence_id", back_populates="intelligence", cascade="all, delete-orphan")
    duplicate_reference = relationship("Intelligence", remote_side="Intelligence.id", foreign_keys=[duplicate_of])
    
    # 索引与表配置
    __table_args__ = (
        Index('idx_intelligence_match_type', 'match_id', 'type_id'),
        Index('idx_intelligence_match_source', 'match_id', 'source_id'),
        Index('idx_intelligence_published_weight', 'published_at', 'calculated_weight'),
        Index('idx_intelligence_status_verified', 'status', 'is_verified'),
        # tags/keywords are Text fields (JSON string payloads). Use regular indexes
        # to keep compatibility across SQLite/PostgreSQL without GIN operator issues.
        Index('idx_intelligence_tags', 'tags'),
        Index('idx_intelligence_keywords', 'keywords'),
        Index('idx_intelligence_popularity', 'popularity_score'),
        Index('idx_intelligence_event_time', 'event_time'),
        Index('idx_intelligence_expiration', 'expiration_at'),
        Index('idx_intelligence_reviewed', 'reviewed_by', 'reviewed_at'),
        Index('idx_intelligence_external_id', 'external_id'),
        CheckConstraint('confidence_score >= 0.0 AND confidence_score <= 1.0', name='ck_confidence_score_range'),
        CheckConstraint('base_weight >= 0.0 AND base_weight <= 1.0', name='ck_base_weight_range'),
        CheckConstraint('weight_multiplier >= 0.5 AND weight_multiplier <= 2.0', name='ck_weight_multiplier_range'),
        CheckConstraint('popularity_score >= 0.0', name='ck_popularity_score_positive'),
        CheckConstraint('trending_score >= 0.0', name='ck_trending_score_positive'),
        {'extend_existing': True}
    )
    
    def __repr__(self) -> str:
        return f"<Intelligence(id={self.id}, match_id={self.match_id}, type={self.type if hasattr(self, 'type') else 'unknown'})>"
    
    def calculate_weight(self) -> float:
        """
        计算情报权重
        
        Returns:
            float: 计算后的权重值 (0-1)
        """
        # 基础权重
        weight = self.base_weight
        
        # 置信度乘数
        confidence_multipliers = {
            ConfidenceLevelEnum.VERY_LOW: 0.2,
            ConfidenceLevelEnum.LOW: 0.4,
            ConfidenceLevelEnum.MEDIUM: 0.6,
            ConfidenceLevelEnum.HIGH: 0.8,
            ConfidenceLevelEnum.VERY_HIGH: 0.9,
            ConfidenceLevelEnum.CONFIRMED: 1.0
        }
        weight *= confidence_multipliers.get(self.confidence, 0.6)
        
        # 重要性乘数
        importance_multipliers = {
            ImportanceLevelEnum.LOW: 0.5,
            ImportanceLevelEnum.MEDIUM: 1.0,
            ImportanceLevelEnum.HIGH: 1.5,
            ImportanceLevelEnum.CRITICAL: 2.0
        }
        weight *= importance_multipliers.get(self.importance, 1.0)
        
        # 来源可信度乘数
        if self.source_info:
            weight *= self.source_info.reliability_score
        
        # 时间衰减因子（如果已发布超过24小时，权重降低）
        if self.published_at:
            hours_since_publish = (datetime.utcnow() - self.published_at).total_seconds() / 3600
            if hours_since_publish > 24:
                time_decay = max(0.5, 1.0 - (hours_since_publish - 24) / 72)  # 24-96小时内线性衰减到0.5
                weight *= time_decay
        
        # 应用权重乘数
        weight *= self.weight_multiplier
        
        # 限制在0-1之间
        self.calculated_weight = max(0.0, min(1.0, weight))
        return self.calculated_weight
    
    def update_popularity(self, view_increment: int = 0, like_increment: int = 0, 
                         comment_increment: int = 0, share_increment: int = 0) -> None:
        """
        更新热门度得分
        
        Args:
            view_increment: 浏览量增量
            like_increment: 点赞量增量
            comment_increment: 评论量增量
            share_increment: 分享量增量
        """
        self.view_count += max(0, view_increment)
        self.like_count += max(0, like_increment)
        self.comment_count += max(0, comment_increment)
        self.share_count += max(0, share_increment)
        
        # 计算热门度得分（加权计算）
        time_factor = 1.0
        if self.created_at:
            hours_since_created = (datetime.utcnow() - self.created_at).total_seconds() / 3600
            time_factor = max(0.1, 1.0 / (1.0 + hours_since_created / 24))  # 24小时衰减一半
        
        self.popularity_score = (
            self.view_count * 0.1 +
            self.like_count * 0.3 +
            self.comment_count * 0.5 +
            self.share_count * 0.8
        ) * time_factor * self.calculated_weight
        
        self.updated_at = datetime.utcnow()

class IntelligenceRelation(Base):
    """
    情报关联模型
    """
    __tablename__ = "intelligence_relations"
    
    id = Column(Integer, primary_key=True, index=True)
    intelligence_id = Column(Integer, ForeignKey("intelligence.id", ondelete="CASCADE"), nullable=False, index=True)
    related_intelligence_id = Column(Integer, ForeignKey("intelligence.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 关联信息
    relation_type = Column(String(50), nullable=False, index=True)  # confirms, contradicts, supports, references
    relation_strength = Column(Float, default=0.5, nullable=False)  # 关联强度 (0-1)
    description = Column(Text, nullable=True)
    
    # 创建信息
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # 关系 - 延迟导入避免循环依赖
    intelligence = relationship("Intelligence", foreign_keys=[intelligence_id], back_populates="related_intelligence")
    related_intelligence = relationship("Intelligence", foreign_keys=[related_intelligence_id])
    
    # 索引
    __table_args__ = (
        Index('idx_intel_relations_intel_type', 'intelligence_id', 'relation_type'),
        Index('idx_intel_relations_both', 'intelligence_id', 'related_intelligence_id', unique=True),
        Index('idx_intel_relations_created', 'created_at'),
        Index('idx_intel_relations_creator', 'created_by'),
        CheckConstraint('relation_strength >= 0.0 AND relation_strength <= 1.0', name='ck_relation_strength_range'),
        CheckConstraint('intelligence_id != related_intelligence_id', name='ck_no_self_reference')
    )
    
    def __repr__(self) -> str:
        return f"<IntelligenceRelation(id={self.id}, intelligence_id={self.intelligence_id}, related_id={self.related_intelligence_id})>"

class IntelligenceAnalytics(Base):
    """
    情报分析模型
    """
    __tablename__ = "intelligence_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 时间信息
    date = Column(Date, nullable=False, index=True)
    hour = Column(Integer, nullable=True)  # 0-23，为NULL表示全天统计
    
    # 统计维度
    intelligence_type = Column(String(50), nullable=True, index=True)
    intelligence_source = Column(String(50), nullable=True, index=True)
    league_id = Column(Integer, nullable=True, index=True)
    
    # 统计指标
    total_items = Column(Integer, default=0, nullable=False)
    verified_items = Column(Integer, default=0, nullable=False)
    high_importance_items = Column(Integer, default=0, nullable=False)  # 高重要性情报数量
    
    # 时效性指标
    avg_response_time = Column(Float, default=0.0, nullable=False)  # 平均响应时间（小时）
    items_within_1h = Column(Integer, default=0, nullable=False)  # 1小时内发布的情报
    items_within_24h = Column(Integer, default=0, nullable=False)  # 24小时内发布的情报
    
    # 质量指标
    avg_confidence_score = Column(Float, default=0.0, nullable=False)  # 平均置信度
    avg_weight = Column(Float, default=0.0, nullable=False)  # 平均权重
    
    # 用户互动指标
    total_views = Column(Integer, default=0, nullable=False)
    total_likes = Column(Integer, default=0, nullable=False)
    total_comments = Column(Integer, default=0, nullable=False)
    total_shares = Column(Integer, default=0, nullable=False)
    
    # 热门度指标
    avg_popularity_score = Column(Float, default=0.0, nullable=False)
    trending_items = Column(Integer, default=0, nullable=False)  # 趋势情报数量（popularity > 0.7）
    
    # 创建时间
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    # 索引
    __table_args__ = (
        Index('idx_intelligence_analytics_date_type', date, intelligence_type),
        Index('idx_intelligence_analytics_date_source', date, intelligence_source),
        Index('idx_intelligence_analytics_date_league', date, league_id),
    )
    
    def __repr__(self) -> str:
        return f"<IntelligenceAnalytics(id={self.id}, date={self.date}, total_items={self.total_items})>"

# 初始化系统情报类型
SYSTEM_INTELLIGENCE_TYPES = [
    # 伤病停赛类
    {"name": "球员伤病", "code": "injury", "category": "player", "default_weight": 0.8, "default_confidence": "medium", "icon": "user-injured"},
    {"name": "球员停赛", "code": "suspension", "category": "player", "default_weight": 0.7, "default_confidence": "high", "icon": "user-slash"},
    
    # 阵容战术类
    {"name": "预计阵容", "code": "lineup", "category": "team", "default_weight": 0.6, "default_confidence": "medium", "icon": "users"},
    {"name": "战术分析", "code": "tactics", "category": "team", "default_weight": 0.5, "default_confidence": "medium", "icon": "chess-board"},
    
    # 环境因素类
    {"name": "天气信息", "code": "weather", "category": "match", "default_weight": 0.4, "default_confidence": "high", "icon": "cloud-sun"},
    {"name": "裁判信息", "code": "referee", "category": "match", "default_weight": 0.4, "default_confidence": "high", "icon": "user-tie"},
    {"name": "场地信息", "code": "venue", "category": "match", "default_weight": 0.3, "default_confidence": "high", "icon": "map-marker-alt"},
    
    # 赔率数据类
    {"name": "赔率变化", "code": "odds", "category": "odds", "default_weight": 0.7, "default_confidence": "high", "icon": "chart-line"},
    
    # 转会传闻类
    {"name": "转会信息", "code": "transfer", "category": "player", "default_weight": 0.5, "default_confidence": "low", "icon": "exchange-alt"},
    {"name": "市场传闻", "code": "rumor", "category": "player", "default_weight": 0.3, "default_confidence": "low", "icon": "comments"},
    
    # 分析预测类
    {"name": "赛前预测", "code": "prediction", "category": "match", "default_weight": 0.6, "default_confidence": "medium", "icon": "crystal-ball"},
    {"name": "统计数据", "code": "statistics", "category": "match", "default_weight": 0.7, "default_confidence": "high", "icon": "chart-bar"},
    
    # 赛前赛后类
    {"name": "赛前预告", "code": "preview", "category": "match", "default_weight": 0.5, "default_confidence": "medium", "icon": "newspaper"},
    {"name": "赛后回顾", "code": "review", "category": "match", "default_weight": 0.5, "default_confidence": "high", "icon": "clipboard-check"},
    
    # 其他类
    {"name": "战意分析", "code": "motivation", "category": "team", "default_weight": 0.6, "default_confidence": "medium", "icon": "fire"},
    {"name": "历史交锋", "code": "history", "category": "match", "default_weight": 0.5, "default_confidence": "high", "icon": "history"},
    {"name": "近期状态", "code": "form", "category": "team", "default_weight": 0.6, "default_confidence": "high", "icon": "trend-up"},
]

# 初始化系统信息来源
SYSTEM_INTELLIGENCE_SOURCES = [
    # 官方渠道
    {"name": "竞彩官方", "code": "official_jc", "source_type": "official", "reliability_score": 0.95, "is_official": True, "is_verified": True},
    {"name": "俱乐部官网", "code": "club_official", "source_type": "official", "reliability_score": 0.9, "is_official": True, "is_verified": True},
    {"name": "联赛官网", "code": "league_official", "source_type": "official", "reliability_score": 0.9, "is_official": True, "is_verified": True},
    
    # 博彩公司
    {"name": "威廉希尔", "code": "william_hill", "source_type": "bookmaker", "reliability_score": 0.85, "is_official": False, "is_verified": True},
    {"name": "立博", "code": "ladbrokes", "source_type": "bookmaker", "reliability_score": 0.85, "is_official": False, "is_verified": True},
    {"name": "bet365", "code": "bet365", "source_type": "bookmaker", "reliability_score": 0.85, "is_official": False, "is_verified": True},
    
    # 权威媒体
    {"name": "ESPN", "code": "espn", "source_type": "media", "reliability_score": 0.8, "is_official": False, "is_verified": True},
    {"name": "天空体育", "code": "sky_sports", "source_type": "media", "reliability_score": 0.8, "is_official": False, "is_verified": True},
    {"name": "BBC体育", "code": "bbc_sport", "source_type": "media", "reliability_score": 0.8, "is_official": False, "is_verified": True},
    
    # 社交媒体
    {"name": "Twitter官方", "code": "twitter_official", "source_type": "social_media", "reliability_score": 0.7, "is_official": False, "is_verified": True},
    {"name": "记者推文", "code": "twitter_journalist", "source_type": "social_media", "reliability_score": 0.6, "is_official": False, "is_verified": True},
    
    # 专家分析
    {"name": "专家分析", "code": "expert_analysis", "source_type": "expert", "reliability_score": 0.7, "is_official": False, "is_verified": True},
    
    # AI分析
    {"name": "AI预测", "code": "ai_prediction", "source_type": "ai_analysis", "reliability_score": 0.6, "is_official": False, "is_verified": True},
    
    # 用户提交
    {"name": "用户提交", "code": "user_submitted", "source_type": "user_submission", "reliability_score": 0.4, "is_official": False, "is_verified": False},
    
    # 系统生成
    {"name": "系统分析", "code": "system_analysis", "source_type": "system", "reliability_score": 0.8, "is_official": False, "is_verified": True},
]
