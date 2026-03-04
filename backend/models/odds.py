"""
赔率数据模型
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, 
    ForeignKey, Float, Text, Enum, CheckConstraint, Index, Date, Time, JSON
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
import enum

from sqlalchemy.ext.mutable import MutableDict
from .base import Base, BaseAuditModel, BaseFullModel


class OddsProviderEnum(enum.Enum):
    """赔率提供商枚举"""
    BET365 = "bet365"
    WILLIAM_HILL = "william_hill"
    LADBROKES = "ladbrokes"
    BETFAIR = "betfair"
    PADDY_POWER = "paddy_power"
    SPORTSBET = "sportsbet"
    UNIBET = "unibet"
    MGM = "mgm"
    FANDUEL = "fanduel"
    DRAFTKINGS = "draftkings"
    OTHER = "other"


class OddsTypeEnum(enum.Enum):
    """赔率类型枚举"""
    WIN_DRAW_LOSS = "win_draw_loss"         # 胜平负
    ASIAN_HANDICAP = "asian_handicap"       # 亚洲盘口
    OVER_UNDER = "over_under"               # 大小球
    BOTH_TEAMS_SCORE = "both_teams_score"   # 双方进球
    CORNERS = "corners"                     # 角球数
    CARDS = "cards"                         # 红黄牌
    CORRECT_SCORE = "correct_score"         # 正确比分
    FIRST_GOAL_SCORER = "first_goal_scorer" # 首粒进球
    ANYTIME_GOAL_SCORER = "anytime_goal_scorer" # 任意进球


class OddsMovementTypeEnum(enum.Enum):
    """赔率变动类型枚举"""
    INCREASE = "increase"                   # 上升
    DECREASE = "decrease"                   # 下降
    STABLE = "stable"                       # 稳定


class Odds(BaseFullModel):
    """
    赔率模型
    """
    __tablename__ = "odds"
    
    # 关联信息
    match_id = Column(Integer, ForeignKey('matches.id', ondelete='CASCADE'), nullable=False, index=True)
    bookmaker_id = Column(Integer, ForeignKey('bookmakers.id', ondelete='CASCADE'), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey('odds_providers.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # 赔率类型
    odds_type = Column(Enum(OddsTypeEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), nullable=False, index=True)
    
    # 基本赔率
    home_win_odds = Column(Float, nullable=True, index=True)      # 主胜赔率
    draw_odds = Column(Float, nullable=True, index=True)          # 平局赔率
    away_win_odds = Column(Float, nullable=True, index=True)      # 客胜赔率
    
    # 让球相关
    asian_handicap_home = Column(Float, nullable=True, index=True)  # 亚盘主队让球
    asian_handicap_away = Column(Float, nullable=True, index=True)  # 亚盘客队让球
    handicap_line = Column(Float, nullable=True, index=True)        # 让球线
    
    # 大小球相关
    over_under_line = Column(Float, nullable=True, index=True)      # 大小球线
    over_odds = Column(Float, nullable=True, index=True)            # 大球赔率
    under_odds = Column(Float, nullable=True, index=True)           # 小球赔率
    
    # 更新时间
    last_updated = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    
    # 状态信息
    is_live = Column(Boolean, default=False, nullable=False, index=True)  # 是否实时赔率
    
    # 市场深度和流动性
    market_depth = Column(MutableDict.as_mutable(Text), default=lambda: {}, nullable=False)      # 市场深度
    liquidity = Column(Float, default=0.0, nullable=False, index=True)  # 流动性
    volume = Column(Float, default=0.0, nullable=False, index=True)     # 交易量
    
    # 波动率
    volatility = Column(Float, default=0.0, nullable=False, index=True)  # 波动率
    
    # 开盘/收盘标识
    is_opening = Column(Boolean, default=False, nullable=False, index=True)  # 是否开盘赔率
    is_closing = Column(Boolean, default=False, nullable=False, index=True)  # 是否收盘赔率
    
    # 外部数据
    external_id = Column(String(100), nullable=True, index=True)      # 外部系统ID
    external_source = Column(String(50), nullable=True, index=True)   # 外部数据来源
    
    # 关系
    match = relationship("Match", back_populates="odds")
    bookmaker = relationship("Bookmaker", back_populates="odds")
    provider = relationship("OddsProvider", back_populates="odds")
    
    # 索引
    __table_args__ = (
        Index('idx_odds_match_type', 'match_id', 'odds_type'),
        Index('idx_odds_bookmaker_match', 'bookmaker_id', 'match_id'),
        Index('idx_odds_provider_match', 'provider_id', 'match_id'),
        Index('idx_odds_last_updated', 'last_updated'),
        Index('idx_odds_is_live', 'is_live'),
        Index('idx_odds_home_win_odds', 'home_win_odds'),
        Index('idx_odds_liquidity', 'liquidity'),
        Index('idx_odds_volatility', 'volatility'),
        {'extend_existing': True}
    )

    def __repr__(self) -> str:
        return f"<Odds(id={self.id}, match_id={self.match_id}, bookmaker_id={self.bookmaker_id}, home={self.home_win_odds}, draw={self.draw_odds}, away={self.away_win_odds})>"

    @property
    def implied_probability_home(self) -> Optional[float]:
        """主胜隐含概率"""
        if self.home_win_odds is not None and self.home_win_odds > 0:
            return 1 / self.home_win_odds
        return None

    @property
    def implied_probability_draw(self) -> Optional[float]:
        """平局隐含概率"""
        if self.draw_odds is not None and self.draw_odds > 0:
            return 1 / self.draw_odds
        return None

    @property
    def implied_probability_away(self) -> Optional[float]:
        """客胜隐含概率"""
        if self.away_win_odds is not None and self.away_win_odds > 0:
            return 1 / self.away_win_odds
        return None

    @property
    def total_implied_probability(self) -> Optional[float]:
        """总隐含概率 (市场公平性指标)"""
        probs = [self.implied_probability_home, self.implied_probability_draw, self.implied_probability_away]
        valid_probs = [p for p in probs if p is not None]
        if valid_probs:
            return sum(valid_probs)
        return None


class OddsMovement(BaseFullModel):
    """
    赔率变动模型
    """
    __tablename__ = "odds_movements"
    
    # 关联信息
    odds_id = Column(Integer, ForeignKey('odds.id', ondelete='CASCADE'), nullable=False, index=True)
    bookmaker_id = Column(Integer, ForeignKey('bookmakers.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # 变动类型
    movement_type = Column(Enum(OddsMovementTypeEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), nullable=False, index=True)
    
    # 变动前后的值
    previous_home_win = Column(Float, nullable=True)
    previous_draw = Column(Float, nullable=True)
    previous_away_win = Column(Float, nullable=True)
    
    current_home_win = Column(Float, nullable=False)
    current_draw = Column(Float, nullable=False)
    current_away_win = Column(Float, nullable=False)
    
    # 变动幅度
    home_change = Column(Float, nullable=True)    # 主胜变化
    draw_change = Column(Float, nullable=True)    # 平局变化
    away_change = Column(Float, nullable=True)    # 客胜变化
    
    # 百分比变化
    home_change_percent = Column(Float, nullable=True)
    draw_change_percent = Column(Float, nullable=True)
    away_change_percent = Column(Float, nullable=True)
    
    # 变动时间
    movement_time = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    
    # 原因
    reason = Column(String(200), nullable=True)   # 变动原因
    
    # 关系
    odds = relationship("Odds")
    bookmaker = relationship("Bookmaker")
    
    # 索引
    __table_args__ = (
        Index('idx_odds_movements_odds_time', 'odds_id', 'movement_time'),
        Index('idx_odds_movements_bookmaker_time', 'bookmaker_id', 'movement_time'),
        Index('idx_odds_movements_type_time', 'movement_type', 'movement_time'),
        Index('idx_odds_movements_movement_time', 'movement_time'),
    )


class Bookmaker(BaseFullModel):
    """
    交易所/博彩商模型
    """
    __tablename__ = "bookmakers"
    
    # 基本信息
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=True)
    
    # 地理信息
    country = Column(String(100), nullable=True, index=True)
    country_code = Column(String(10), nullable=True, index=True)
    license_info = Column(String(200), nullable=True)
    
    # 网络信息
    website = Column(String(200), nullable=True)
    logo_url = Column(String(500), nullable=True)
    
    # 状态信息
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_reputable = Column(Boolean, default=True, nullable=False, index=True)
    
    # 评级
    reputation_score = Column(Float, default=0.0, nullable=False, index=True)
    
    # 支持的市场
    supported_markets = Column(Text, default='[]', nullable=False)  # 存储为JSON数组字符串
    
    # 配置信息
    config = Column(MutableDict.as_mutable(Text), default=lambda: {}, nullable=False)
    
    # 关系
    odds = relationship("Odds", back_populates="bookmaker", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_bookmakers_active', 'is_active'),
        Index('idx_bookmakers_reputable', 'is_reputable'),
        Index('idx_bookmakers_country', 'country'),
        Index('idx_bookmakers_reputation', 'reputation_score'),
        {'extend_existing': True}
    )
    
    def __repr__(self) -> str:
        return f"<Bookmaker(id={self.id}, name='{self.name}', code='{self.code}')>"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "full_name": self.full_name,
            "country": self.country,
            "country_code": self.country_code,
            "license_info": self.license_info,
            "website": self.website,
            "logo_url": self.logo_url,
            "is_active": self.is_active,
            "is_reputable": self.is_reputable,
            "reputation_score": self.reputation_score,
            "supported_markets": self.supported_markets,
            "config": self.config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class OddsProvider(BaseFullModel):
    """
    赔率提供商模型
    """
    __tablename__ = "odds_providers"
    
    # 基本信息
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=True)
    
    # 地理信息
    country = Column(String(100), nullable=True, index=True)
    country_code = Column(String(10), nullable=True, index=True)
    
    # 网络信息
    website = Column(String(200), nullable=True)
    api_endpoint = Column(String(200), nullable=True)
    api_key = Column(String(200), nullable=True)
    
    # 状态信息
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    reliability_score = Column(Float, default=0.0, nullable=False, index=True)
    
    # 配置信息
    config = Column(MutableDict.as_mutable(Text), default=lambda: {}, nullable=False)
    
    # 关系
    odds = relationship("Odds", back_populates="provider", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_odds_providers_active', 'is_active'),
        {'extend_existing': True}
    )
    
    def __repr__(self) -> str:
        return f"<OddsProvider(id={self.id}, name='{self.name}', code='{self.code}')>"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "full_name": self.full_name,
            "country": self.country,
            "country_code": self.country_code,
            "website": self.website,
            "api_endpoint": self.api_endpoint,
            "is_active": self.is_active,
            "reliability_score": self.reliability_score,
            "config": self.config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }