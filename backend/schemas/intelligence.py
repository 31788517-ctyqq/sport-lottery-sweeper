"""
情报相关数据模式
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
import enum


class IntelligenceType(str, enum.Enum):
    """
    情报类型枚举
    """
    INJURY = "injury"                    # 伤病信息
    SUSPENSION = "suspension"            # 停赛信息
    WEATHER = "weather"                  # 天气影响
    REFEREES = "referees"               # 裁判信息
    MOTIVATION = "motivation"            # 球队战意
    SCHEDULE = "schedule"                # 赛程密度
    TACTICS = "tactics"                 # 战术变化
    COACH = "coach"                     # 教练变动
    HISTORY = "head_to_head"             # 历史交锋
    PREDICTION = "prediction"            # 比赛预测
    ATMOSPHERE = "atmosphere"            # 氛围影响
    OTHER = "other"                      # 其他信息


class IntelligenceSource(str, enum.Enum):
    """
    情报来源枚举
    """
    OFFICIAL = "official"      # 官方消息
    MEDIA = "media"            # 媒体报道
    SOCIAL = "social"          # 社交媒体
    BOOKMAKER = "bookmaker"    # 赔率变化


class IntelligenceSourceResponse(BaseModel):
    """
    情报来源响应模型
    """
    source: str
    description: str
    count: int


class IntelligenceFilter(BaseModel):
    """
    情报筛选模型
    """
    intelligence_type: Optional[IntelligenceType] = None
    source: Optional[IntelligenceSource] = None
    min_reliability: Optional[float] = None
    impact_level: Optional[str] = None
    related_teams: Optional[List[str]] = None
    match_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class IntelligenceTypeResponse(BaseModel):
    """
    情报类型响应模型
    """
    type: str
    description: str
    count: int


class IntelligenceBase(BaseModel):
    """
    情报基础模型
    """
    title: str
    content: str
    intelligence_type: IntelligenceType
    source: IntelligenceSource
    reliability: float  # 可靠性评分，0-1之间
    impact_level: str   # 影响级别 high, medium, low
    related_teams: Optional[List[str]] = []
    related_players: Optional[List[str]] = []


class IntelligenceCreate(IntelligenceBase):
    """
    情报创建模型
    """
    match_id: int
    expires_at: Optional[datetime] = None


class IntelligenceUpdate(IntelligenceBase):
    """
    情报更新模型
    """
    title: Optional[str] = None
    content: Optional[str] = None
    intelligence_type: Optional[IntelligenceType] = None
    source: Optional[IntelligenceSource] = None
    reliability: Optional[float] = None
    impact_level: Optional[str] = None
    related_teams: Optional[List[str]] = None
    related_players: Optional[List[str]] = None
    is_active: Optional[bool] = None


class IntelligenceResponse(IntelligenceBase):
    """
    情报响应模型
    """
    id: int
    match_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    expires_at: Optional[datetime] = None

    class Config:
        model_config = ConfigDict()


class IntelligenceList(BaseModel):
    """
    情报列表响应模型
    """
    items: list[IntelligenceResponse]
    total: int
    page: int
    size: int
    pages: int


class IntelligenceAnalytics(BaseModel):
    """
    情报分析模型
    """
    type_distribution: dict
    source_reliability: dict
    impact_analysis: dict
    trend_over_time: list