"""
比赛、球队、联赛数据模型
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, 
    ForeignKey, Float, Text, Enum, Date, Time,
    CheckConstraint, Index, JSON
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
import enum

from sqlalchemy.ext.mutable import MutableDict
from .base import Base, BaseAuditModel, BaseFullModel

# 比赛状态枚举
class MatchStatusEnum(enum.Enum):
    """比赛状态枚举"""
    SCHEDULED = "scheduled"      # 已安排
    LIVE = "live"                # 进行中
    HALFTIME = "halftime"        # 中场休息
    FINISHED = "finished"        # 已结束
    POSTPONED = "postponed"      # 延期
    CANCELLED = "cancelled"      # 取消
    ABANDONED = "abandoned"      # 中止
    SUSPENDED = "suspended"      # 暂停

# 比赛类型枚举
class MatchTypeEnum(enum.Enum):
    """比赛类型枚举"""
    LEAGUE = "league"            # 联赛
    CUP = "cup"                  # 杯赛
    FRIENDLY = "friendly"        # 友谊赛
    QUALIFIER = "qualifier"      # 资格赛
    PLAYOFF = "playoff"          # 季后赛
    FINAL = "final"              # 决赛

# 比赛重要性枚举
class MatchImportanceEnum(enum.Enum):
    """比赛重要性枚举"""
    LOW = "low"                  # 低重要性
    MEDIUM = "medium"            # 中重要性
    HIGH = "high"                # 高重要性
    VERY_HIGH = "very_high"      # 非常重要

class League(BaseFullModel):
    """
    联赛模型
    """
    __tablename__ = "leagues"
    __table_args__ = {'extend_existing': True}  # 添加此选项以允许扩展已存在的表
    
    # 基本信息
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    short_name = Column(String(50), nullable=True)
    
    # 描述信息
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    banner_url = Column(String(500), nullable=True)
    
    # 国家/地区信息
    country = Column(String(100), nullable=False, index=True)
    country_code = Column(String(10), nullable=False, index=True)
    region = Column(String(100), nullable=True)
    
    # 联赛属性
    level = Column(Integer, default=1, nullable=False, index=True)  # 联赛级别（1最高）
    type = Column(String(50), nullable=False, index=True)  # national, international, regional
    format = Column(String(50), nullable=True)  # round_robin, knockout, hybrid
    
    # 赛季信息
    current_season = Column(String(50), nullable=True)
    season_start = Column(Date, nullable=True)
    season_end = Column(Date, nullable=True)
    total_teams = Column(Integer, default=0, nullable=False)
    total_matches = Column(Integer, default=0, nullable=False)
    
    # 状态信息
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_popular = Column(Boolean, default=False, nullable=False, index=True)
    is_national = Column(Boolean, default=False, nullable=False)
    
    # 外部数据
    external_id = Column(String(100), nullable=True, index=True)  # 外部系统ID
    external_source = Column(String(50), nullable=True, index=True)  # 外部数据来源
    
    # 统计信息
    total_views = Column(Integer, default=0, nullable=False, index=True)
    total_followers = Column(Integer, default=0, nullable=False, index=True)
    average_attendance = Column(Integer, default=0, nullable=False)
    
    # 配置信息
    config = Column(MutableDict.as_mutable(Text), default=lambda: {}, nullable=False)  # 联赛配置
    
    # 关系
    matches = relationship("Match", back_populates="league", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="league", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_leagues_country_active', 'country', 'is_active'),
        Index('idx_leagues_level_type', 'level', 'type'),
        Index('idx_leagues_popular_active', 'is_popular', 'is_active'),
        {'extend_existing': True}  # 确保支持表扩展
    )


class Team(BaseFullModel):
    """
    球队模型
    """
    __tablename__ = "teams"
    __table_args__ = {'extend_existing': True}  # 添加此选项以允许扩展已存在的表
    
    # 基本信息
    name = Column(String(100), nullable=False, index=True)
    short_name = Column(String(50), nullable=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=True)
    
    # 描述信息
    description = Column(Text, nullable=True)
    website = Column(String(200), nullable=True)
    
    # 国家/地区信息
    country = Column(String(100), nullable=False, index=True)
    country_code = Column(String(10), nullable=False, index=True)
    city = Column(String(100), nullable=True)
    
    # 历史信息
    founded_year = Column(Integer, nullable=True, index=True)  # 成立年份
    
    # 场馆信息
    stadium = Column(String(200), nullable=True)  # 主场
    
    # 人员信息
    coach = Column(String(100), nullable=True)
    owner = Column(String(100), nullable=True)
    
    # 图片资源
    logo_url = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
    jersey_home_url = Column(String(500), nullable=True)  # 主场球衣
    jersey_away_url = Column(String(500), nullable=True)  # 客场球衣
    
    # 颜色信息
    primary_color = Column(String(20), nullable=True)  # 主色调
    secondary_color = Column(String(20), nullable=True)  # 辅助色
    
    # 属性信息
    is_national_team = Column(Boolean, default=False, nullable=False, index=True)  # 是否国家队
    
    # 联赛信息
    league_id = Column(Integer, ForeignKey('leagues.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # 状态信息
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_popular = Column(Boolean, default=False, nullable=False, index=True)
    
    # 统计信息
    total_players = Column(Integer, default=0, nullable=False)
    total_views = Column(Integer, default=0, nullable=False, index=True)
    total_followers = Column(Integer, default=0, nullable=False, index=True)
    
    # 外部数据
    external_id = Column(String(100), nullable=True, index=True)  # 外部系统ID
    external_source = Column(String(50), nullable=True, index=True)  # 外部数据来源
    
    # 配置信息
    config = Column(MutableDict.as_mutable(Text), default=lambda: {}, nullable=False)  # 球队配置
    
    # 关系
    league = relationship("League", back_populates="teams")
    home_matches = relationship("Match", foreign_keys='Match.home_team_id', back_populates="home_team")
    away_matches = relationship("Match", foreign_keys='Match.away_team_id', back_populates="away_team")
    players = relationship("Player", back_populates="team", cascade="all, delete-orphan")
    intelligence_items = relationship("Intelligence", back_populates="team", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_teams_country_active', 'country', 'is_active'),
        Index('idx_teams_league_active', 'league_id', 'is_active'),
        Index('idx_teams_popular_active', 'is_popular', 'is_active'),
        {'extend_existing': True}  # 确保支持表扩展
    )


class Match(BaseFullModel):
    """
    比赛模型
    """
    __tablename__ = "matches"
    __table_args__ = {'extend_existing': True}  # 添加此选项以允许扩展已存在的表
    
    # 比赛标识
    match_identifier = Column(String(50), unique=True, nullable=False, index=True)  # 比赛唯一标识符
    
    # 球队信息
    home_team_id = Column(Integer, ForeignKey('teams.id', ondelete='SET NULL'), nullable=True, index=True)
    away_team_id = Column(Integer, ForeignKey('teams.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # 联赛信息
    league_id = Column(Integer, ForeignKey('leagues.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # 场馆信息
    venue_id = Column(Integer, ForeignKey('venues.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # 时间信息
    match_date = Column(Date, nullable=False, index=True)  # 比赛日期
    match_time = Column(Time, nullable=False)  # 比赛时间
    scheduled_kickoff = Column(DateTime(timezone=True), nullable=False, index=True)  # 计划开球时间
    
    # 状态信息
    status = Column(Enum(MatchStatusEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), default=MatchStatusEnum.SCHEDULED, nullable=False, index=True)
    
    # 比赛分类信息
    match_day = Column(String(20), nullable=True, index=True)  # 比赛日 (第几轮)
    match_week = Column(String(20), nullable=True, index=True)  # 比赛周
    season = Column(String(20), nullable=True, index=True)  # 赛季
    round_number = Column(Integer, nullable=True, index=True)  # 轮次
    group_name = Column(String(50), nullable=True, index=True)  # 组别名称
    
    # 重要性信息
    importance = Column(Enum(MatchImportanceEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), default=MatchImportanceEnum.MEDIUM, nullable=False, index=True)
    type = Column(Enum(MatchTypeEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False), default=MatchTypeEnum.LEAGUE, nullable=False, index=True)
    
    # 比赛统计信息
    attendance = Column(Integer, nullable=True)  # 观众人数
    referee = Column(String(100), nullable=True)  # 裁判
    
    # 天气信息
    weather_conditions = Column(String(100), nullable=True)  # 天气状况
    
    # 比赛结果信息
    home_score = Column(Integer, nullable=True)  # 主队得分
    away_score = Column(Integer, nullable=True)  # 客队得分
    halftime_score = Column(String(10), nullable=True)  # 半场比分 (格式: "1-0")
    fulltime_result = Column(String(10), nullable=True)  # 全场结果 (格式: "H/D/A")
    
    # 比赛报告
    match_report = Column(Text, nullable=True)  # 比赛报告
    
    # 发布状态
    is_published = Column(Boolean, default=True, nullable=False, index=True)
    is_featured = Column(Boolean, default=False, nullable=False, index=True)
    
    # 优先级
    priority = Column(Integer, default=0, nullable=False, index=True)
    
    # 统计信息
    popularity = Column(Integer, default=0, nullable=False, index=True)  # 受欢迎程度
    
    # 外部数据
    external_id = Column(String(100), nullable=True, index=True)  # 外部系统ID
    external_source = Column(String(50), nullable=True, index=True)  # 外部数据来源
    
    # 配置信息
    config = Column(MutableDict.as_mutable(Text), default=lambda: {}, nullable=False)  # 比赛配置
    
    # 关系
    league = relationship("League", back_populates="matches")
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    venue = relationship("Venue", back_populates="matches")
    intelligence_items = relationship("Intelligence", back_populates="match", cascade="all, delete-orphan", overlaps="intelligence")
    odds = relationship("Odds", back_populates="match", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="match", cascade="all, delete-orphan")
    lineups = relationship("MatchLineup", back_populates="match", cascade="all, delete-orphan")
    events = relationship("MatchEvent", back_populates="match", cascade="all, delete-orphan")
    intelligence = relationship("Intelligence", back_populates="match", cascade="all, delete-orphan", viewonly=True)

    # 索引
    __table_args__ = (
        Index('idx_matches_status_date', 'status', 'match_date'),
        Index('idx_matches_league_date', 'league_id', 'match_date'),
        Index('idx_matches_teams_date', 'home_team_id', 'away_team_id', 'match_date'),
        Index('idx_matches_venue_date', 'venue_id', 'match_date'),
        Index('idx_matches_published_date', 'is_published', 'match_date'),
        Index('idx_matches_type_importance', 'type', 'importance'),
        {'extend_existing': True}  # 确保支持表扩展
    )
    
    def __repr__(self) -> str:
        return f"<Match(id={self.id}, {self.home_team.name} vs {self.away_team.name}, {self.match_time})>"
    
    @property
    def is_finished(self) -> bool:
        """比赛是否已结束"""
        return self.status == MatchStatusEnum.FINISHED
    
    @property
    def is_live(self) -> bool:
        """比赛是否正在进行"""
        return self.status in [MatchStatusEnum.LIVE, MatchStatusEnum.HALFTIME]
    
    @property
    def winner(self) -> Optional[str]:
        """获取获胜方"""
        if not self.is_finished or self.home_score is None or self.away_score is None:
            return None
        
        if self.home_score > self.away_score:
            return "home"
        elif self.away_score > self.home_score:
            return "away"
        else:
            return "draw"
            
    @property
    def result_summary(self) -> str:
        """获取比赛结果摘要"""
        if self.status == MatchStatusEnum.SCHEDULED:
            return "未开始"
        elif self.status == MatchStatusEnum.LIVE:
            return f"直播中: {self.home_score or 0}-{self.away_score or 0}"
        elif self.status == MatchStatusEnum.HALFTIME:
            return f"中场: {self.home_score_ht or 0}-{self.away_score_ht or 0}"
        elif self.status == MatchStatusEnum.FINISHED:
            if self.home_score > self.away_score:
                return f"主胜: {self.home_score}-{self.away_score}"
            elif self.away_score > self.home_score:
                return f"客胜: {self.home_score}-{self.away_score}"
            else:
                return f"平局: {self.home_score}-{self.away_score}"
        else:
            return self.status.value
    
    def update_score(self, home_score: int, away_score: int) -> None:
        """更新比分"""
        self.home_score = home_score
        self.away_score = away_score
        
        # 更新全场结果
        if home_score > away_score:
            self.fulltime_result = 'H'
        elif away_score > home_score:
            self.fulltime_result = 'A'
        else:
            self.fulltime_result = 'D'
            
        self.updated_at = datetime.utcnow()

class Player(BaseFullModel):
    """
    球员模型
    """
    __tablename__ = "players"
    
    # 基本信息
    name = Column(String(100), nullable=False, index=True)
    full_name = Column(String(200), nullable=True)
    
    # 个人信息
    date_of_birth = Column(Date, nullable=True)
    nationality = Column(String(100), nullable=True, index=True)
    nationality_code = Column(String(10), nullable=True, index=True)
    
    # 身体信息
    height = Column(Integer, nullable=True)  # 厘米
    weight = Column(Integer, nullable=True)  # 公斤
    preferred_foot = Column(String(10), nullable=True)  # left, right, both
    
    # 位置信息
    position = Column(String(50), nullable=False, index=True)  # GK, DF, MF, FW
    position_detail = Column(String(50), nullable=True)  # CB, LB, RB, CM, LW, ST, etc.
    
    # 球衣号码
    jersey_number = Column(Integer, nullable=True)
    
    # 所属球队
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # 状态信息
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_injured = Column(Boolean, default=False, nullable=False, index=True)
    injury_details = Column(Text, nullable=True)
    
    # 合同信息
    contract_start = Column(Date, nullable=True)
    contract_end = Column(Date, nullable=True)
    market_value = Column(Float, nullable=True)  # 市场价值（欧元）
    
    # 外部数据
    external_id = Column(String(100), nullable=True, index=True)
    external_source = Column(String(50), nullable=True)
    
    # 统计信息
    total_appearances = Column(Integer, default=0, nullable=False)
    total_goals = Column(Integer, default=0, nullable=False)
    total_assists = Column(Integer, default=0, nullable=False)
    total_yellow_cards = Column(Integer, default=0, nullable=False)
    total_red_cards = Column(Integer, default=0, nullable=False)
    
    # 社交媒体
    image_url = Column(String(500), nullable=True)
    
    # 关系
    team = relationship("Team", back_populates="players")
    lineups = relationship("MatchLineup", back_populates="player", cascade="all, delete-orphan")
    events = relationship("MatchEvent", back_populates="player", cascade="all, delete-orphan")
    intelligence_items = relationship("Intelligence", back_populates="player", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_players_team_position', team_id, position),
        Index('idx_players_nationality_position', nationality, position),
        Index('idx_players_is_active_is_injured', is_active, is_injured),
    )
    
    def __repr__(self) -> str:
        return f"<Player(id={self.id}, name={self.name}, position={self.position})>"
    
    @property
    def age(self) -> Optional[int]:
        """计算球员年龄"""
        if not self.date_of_birth:
            return None
        
        today = datetime.utcnow().date()
        born = self.date_of_birth
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

class MatchLineup(Base):
    """
    比赛阵容模型
    """
    __tablename__ = "match_lineups"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 阵容信息
    is_starting = Column(Boolean, default=False, nullable=False, index=True)  # 是否首发
    position = Column(String(50), nullable=False)  # 场上位置
    jersey_number = Column(Integer, nullable=True)
    
    # 比赛信息
    minutes_played = Column(Integer, default=0, nullable=False)  # 出场分钟数
    substitution_minute = Column(Integer, nullable=True)  # 换人时间（分钟）
    substitution_type = Column(String(20), nullable=True)  # in, out
    
    # 统计信息
    goals = Column(Integer, default=0, nullable=False)
    assists = Column(Integer, default=0, nullable=False)
    yellow_cards = Column(Integer, default=0, nullable=False)
    red_cards = Column(Integer, default=0, nullable=False)
    shots = Column(Integer, default=0, nullable=False)
    shots_on_target = Column(Integer, default=0, nullable=False)
    passes = Column(Integer, default=0, nullable=False)
    passes_completed = Column(Integer, default=0, nullable=False)
    tackles = Column(Integer, default=0, nullable=False)
    interceptions = Column(Integer, default=0, nullable=False)
    
    # 评分
    rating = Column(Float, nullable=True)  # 球员评分
    
    # 关系
    match = relationship("Match", back_populates="lineups")
    player = relationship("Player", back_populates="lineups")
    team = relationship("Team")
    
    # 索引
    __table_args__ = (
        Index('idx_match_lineups_match_team', match_id, team_id),
        Index('idx_match_lineups_player_match', player_id, match_id),
        Index('idx_match_lineups_is_starting', is_starting),
    )
    
    def __repr__(self) -> str:
        return f"<MatchLineup(id={self.id}, match_id={self.match_id}, player_id={self.player_id})>"

class MatchEvent(Base):
    """
    比赛事件模型
    """
    __tablename__ = "match_events"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 事件信息
    event_type = Column(String(50), nullable=False, index=True)  # goal, yellow_card, red_card, substitution, etc.
    minute = Column(Integer, nullable=False, index=True)  # 事件发生时间（分钟）
    extra_minute = Column(Integer, nullable=True)  # 补时时间
    
    # 相关球员
    player_id = Column(Integer, ForeignKey("players.id", ondelete="SET NULL"), nullable=True, index=True)
    player_name = Column(String(100), nullable=True)
    
    # 相关球队
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # 事件详情
    details = Column(MutableDict.as_mutable(Text), default=lambda: {}, nullable=False)
    description = Column(Text, nullable=True)
    
    # 创建时间
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # 关系
    match = relationship("Match", back_populates="events")
    player = relationship("Player", back_populates="events")
    team = relationship("Team")
    
    # 索引
    __table_args__ = (
        Index('idx_match_events_match_minute', match_id, minute),
        Index('idx_match_events_type_minute', event_type, minute),
        Index('idx_match_events_player_match', player_id, match_id),
    )
    
    def __repr__(self) -> str:
        return f"<MatchEvent(id={self.id}, match_id={self.match_id}, event_type={self.event_type})>"

# 初始化常用联赛数据
POPULAR_LEAGUES = [
    # 欧洲联赛
    {"name": "英格兰超级联赛", "code": "premier_league", "country": "英格兰", "country_code": "ENG", "level": 1, "is_popular": True},
    {"name": "西班牙甲级联赛", "code": "la_liga", "country": "西班牙", "country_code": "ESP", "level": 1, "is_popular": True},
    {"name": "德国甲级联赛", "code": "bundesliga", "country": "德国", "country_code": "GER", "level": 1, "is_popular": True},
    {"name": "意大利甲级联赛", "code": "serie_a", "country": "意大利", "country_code": "ITA", "level": 1, "is_popular": True},
    {"name": "法国甲级联赛", "code": "ligue_1", "country": "法国", "country_code": "FRA", "level": 1, "is_popular": True},
    
    # 亚洲联赛
    {"name": "中国超级联赛", "code": "csl", "country": "中国", "country_code": "CHN", "level": 1, "is_popular": True},
    {"name": "日本职业足球联赛", "code": "j_league", "country": "日本", "country_code": "JPN", "level": 1, "is_popular": True},
    {"name": "韩国K联赛", "code": "k_league", "country": "韩国", "country_code": "KOR", "level": 1, "is_popular": True},
    
    # 国际赛事
    {"name": "欧洲冠军联赛", "code": "champions_league", "country": "欧洲", "country_code": "EUR", "level": 0, "is_popular": True},
    {"name": "欧洲联赛", "code": "europa_league", "country": "欧洲", "country_code": "EUR", "level": 1, "is_popular": True},
    {"name": "世界杯", "code": "world_cup", "country": "国际", "country_code": "INT", "level": 0, "is_popular": True},
    {"name": "欧洲杯", "code": "euro_cup", "country": "欧洲", "country_code": "EUR", "level": 0, "is_popular": True},
]