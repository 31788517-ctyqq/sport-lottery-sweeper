"""
比赛信息相关Schema定义
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MatchBase(BaseModel):
    match_id: str = Field(..., max_length=50, description="比赛唯一标识")
    home_team: str = Field(..., max_length=100, description="主队名称")
    away_team: str = Field(..., max_length=100, description="客队名称")
    match_time: datetime = Field(..., description="比赛时间")
    league: Optional[str] = Field(None, max_length=100, description="联赛/杯赛")
    status: Optional[str] = Field("pending", max_length=20, description="比赛状态: pending/ongoing/finished")
    home_score: Optional[int] = Field(None, description="主队得分")
    away_score: Optional[int] = Field(None, description="客队得分")
    final_result: Optional[str] = Field(None, max_length=20, description="最终赛果")


class MatchCreate(MatchBase):
    pass


class MatchUpdate(BaseModel):
    home_team: Optional[str] = Field(None, max_length=100)
    away_team: Optional[str] = Field(None, max_length=100)
    match_time: Optional[datetime] = None
    league: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, max_length=20)
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    final_result: Optional[str] = Field(None, max_length=20)


class MatchResponse(MatchBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MatchListResponse(BaseModel):
    items: List[MatchResponse]
    total: int
    page: int
    size: int


# 为向后兼容提供别名
Match = MatchResponse