from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from pydantic.config import ConfigDict


class FilterRequest(BaseModel):
    """
    北单过滤请求参数
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "strength": ["+1", "+2"],
                "winLevel": ["3", "4"],
                "stability": ["S", "A"],
                "source": "beidan"
            }
        }
    )
    
    strength: Optional[List[str]] = []
    winLevel: Optional[List[str]] = []
    stability: Optional[List[str]] = []
    source: Optional[str] = "beidan"


class FilterOptionResponse(BaseModel):
    options: Dict[str, Any]


class MatchData(BaseModel):
    id: str
    match_id: str
    home_team: str
    away_team: str
    league: str
    match_time: str
    power_home: float
    power_away: float
    win_pan_home: float
    win_pan_away: float
    odds_home: float
    odds_away: float
    odds_draw: float
    stability: float
    power_diff: float
    win_pan_diff: float
    p_level: int
    delta_wp: float
    rq: int
    home_feature: str
    away_feature: str
    home_spf: str
    away_spf: str
    data_source: str


class FilterResultResponse(BaseModel):
    matches: List[MatchData]
    total: int


# 兼容旧名称
BeidanFilterRequest = FilterRequest