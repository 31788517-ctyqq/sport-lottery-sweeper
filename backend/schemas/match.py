"""
比赛相关数据模式
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict


class MatchBase(BaseModel):
    """
    比赛基础模型
    """
    home_team: str
    away_team: str
    league: str
    match_date: datetime
    venue: Optional[str] = None


class MatchCreate(MatchBase):
    """
    比赛建立模型
    """
    odds_home: Optional[float] = None
    odds_draw: Optional[float] = None
    odds_away: Optional[float] = None


class MatchUpdate(BaseModel):
    """
    比赛更新模型
    """
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    league: Optional[str] = None
    match_date: Optional[datetime] = None
    venue: Optional[str] = None
    odds_home: Optional[float] = None
    odds_draw: Optional[float] = None
    odds_away: Optional[float] = None


class MatchResponse(MatchBase):
    """
    比赛响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    status: str  # pending, live, finished, cancelled
    score_home: Optional[int] = None
    score_away: Optional[int] = None

    class Config(SettingsConfigDict):
        from_attributes = True


class PublicMatchResponse(BaseModel):
    """
    公共比赛响应模型，用于前端展示
    """
    id: str
    match_id: str
    home_team: str
    away_team: str
    league: str
    match_date: str
    match_time: str
    odds_home_win: float
    odds_draw: float
    odds_away_win: float
    status: str
    popularity: int
    predicted_result: str
    prediction_confidence: float


class MatchList(BaseModel):
    """
    比赛列表响应模型
    """
    items: list[MatchResponse]
    total: int
    page: int
    size: int
    pages: int


# 为admin模块添加缺失的类
class TeamBase(BaseModel):
    """
    球队基础模型
    """
    name: str
    short_name: str
    country: str
    logo_url: Optional[str] = None


class TeamCreate(TeamBase):
    """
    球队创建模型
    """
    pass


class TeamUpdate(BaseModel):
    """
    球队更新模型
    """
    name: Optional[str] = None
    short_name: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None


class TeamResponse(TeamBase):
    """
    球队响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config(SettingsConfigDict):
        from_attributes = True


class LeagueBase(BaseModel):
    """
    联赛基础模型
    """
    name: str
    country: str
    level: int
    logo_url: Optional[str] = None


class LeagueCreate(LeagueBase):
    """
    联赛创建模型
    """
    pass


class LeagueUpdate(BaseModel):
    """
    联赛更新模型
    """
    name: Optional[str] = None
    country: Optional[str] = None
    level: Optional[int] = None
    logo_url: Optional[str] = None


class LeagueResponse(LeagueBase):
    """
    联赛响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config(SettingsConfigDict):
        from_attributes = True

# Updated import to use relative path
from ..schemas.match import MatchCreate
