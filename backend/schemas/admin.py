"""
Admin相关的Pydantic模型
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MatchResponse(BaseModel):
    """比赛响应模型"""
    id: int
    match_id: str
    home_team: str
    away_team: str
    league: str
    match_date: datetime
    odds_home_win: Optional[float] = None
    odds_draw: Optional[float] = None
    odds_away_win: Optional[float] = None
    status: str
    popularity: int

    class Config:
        from_attributes = True


class CreateMatchRequest(BaseModel):
    """创建比赛请求模型"""
    match_id: str
    home_team: str
    away_team: str
    league: str
    match_date: datetime
    odds_home_win: Optional[float] = None
    odds_draw: Optional[float] = None
    odds_away_win: Optional[float] = None
    status: str = "scheduled"
    popularity: int = 50


class UpdateMatchRequest(BaseModel):
    """更新比赛请求模型"""
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    league: Optional[str] = None
    match_date: Optional[datetime] = None
    odds_home_win: Optional[float] = None
    odds_draw: Optional[float] = None
    odds_away_win: Optional[float] = None
    status: Optional[str] = None
    popularity: Optional[int] = None