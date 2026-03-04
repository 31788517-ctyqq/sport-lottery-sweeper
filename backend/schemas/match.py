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


# 添加MatchCreateUpdate类
class MatchCreateUpdate(BaseModel):
    match_id: Optional[str] = Field(None, max_length=50, description="比赛唯一标识")
    home_team: Optional[str] = Field(None, max_length=100, description="主队名称")
    away_team: Optional[str] = Field(None, max_length=100, description="客队名称")
    match_time: Optional[datetime] = Field(None, description="比赛时间")
    league: Optional[str] = Field(None, max_length=100, description="联赛/杯赛")
    status: Optional[str] = Field(None, max_length=20, description="比赛状态: pending/ongoing/finished")
    home_score: Optional[int] = Field(None, description="主队得分")
    away_score: Optional[int] = Field(None, description="客队得分")
    final_result: Optional[str] = Field(None, max_length=20, description="最终赛果")


# 添加MatchFilter类
class MatchFilter(BaseModel):
    league: Optional[str] = Field(None, description="联赛筛选")
    status: Optional[str] = Field(None, description="状态筛选")
    date_from: Optional[datetime] = Field(None, description="开始日期")
    date_to: Optional[datetime] = Field(None, description="结束日期")
    keyword: Optional[str] = Field(None, description="关键词搜索")


# 为向后兼容提供别名
Match = MatchResponse


# 联赛相关Schema定义
class LeagueBase(BaseModel):
    name: str = Field(..., max_length=100, description="联赛名称")
    code: str = Field(..., max_length=50, description="联赛代码")
    short_name: Optional[str] = Field(None, max_length=50, description="联赛简称")
    description: Optional[str] = Field(None, description="联赛描述")
    logo_url: Optional[str] = Field(None, description="联赛Logo URL")
    banner_url: Optional[str] = Field(None, description="联赛横幅URL")
    country: str = Field(..., max_length=100, description="国家/地区")
    country_code: str = Field(..., max_length=10, description="国家/地区代码")
    region: Optional[str] = Field(None, max_length=100, description="地区")
    level: int = Field(1, ge=1, description="联赛级别（1最高）")
    type: str = Field(..., max_length=50, description="联赛类型: national, international, regional")
    format: Optional[str] = Field(None, max_length=50, description="联赛形式: round_robin, knockout, hybrid")
    current_season: Optional[str] = Field(None, max_length=50, description="当前赛季")
    season_start: Optional[str] = Field(None, description="赛季开始日期")
    season_end: Optional[str] = Field(None, description="赛季结束日期")
    total_teams: int = Field(0, ge=0, description="总球队数")
    total_matches: int = Field(0, ge=0, description="总比赛数")
    is_active: bool = Field(True, description="是否激活")
    is_popular: bool = Field(False, description="是否热门")
    is_national: bool = Field(False, description="是否国家队赛事")
    external_id: Optional[str] = Field(None, max_length=100, description="外部系统ID")
    external_source: Optional[str] = Field(None, max_length=50, description="外部数据来源")
    config: Optional[dict] = Field(None, description="联赛配置")


class LeagueCreate(LeagueBase):
    pass


class LeagueUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    code: Optional[str] = Field(None, max_length=50)
    short_name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None)
    logo_url: Optional[str] = Field(None)
    banner_url: Optional[str] = Field(None)
    country: Optional[str] = Field(None, max_length=100)
    country_code: Optional[str] = Field(None, max_length=10)
    region: Optional[str] = Field(None, max_length=100)
    level: Optional[int] = Field(None, ge=1)
    type: Optional[str] = Field(None, max_length=50)
    format: Optional[str] = Field(None, max_length=50)
    current_season: Optional[str] = Field(None, max_length=50)
    season_start: Optional[str] = Field(None)
    season_end: Optional[str] = Field(None)
    total_teams: Optional[int] = Field(None, ge=0)
    total_matches: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = Field(None)
    is_popular: Optional[bool] = Field(None)
    is_national: Optional[bool] = Field(None)
    external_id: Optional[str] = Field(None, max_length=100)
    external_source: Optional[str] = Field(None, max_length=50)
    config: Optional[dict] = Field(None)


class LeagueResponse(LeagueBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LeagueListResponse(BaseModel):
    items: List[LeagueResponse]
    total: int
    page: int
    size: int
