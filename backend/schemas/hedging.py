from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


class HedgingOpportunityBase(BaseModel):
    match_combination_id: str
    match1_id: int
    match1_home_team: str
    match1_away_team: str
    match1_start_time: datetime
    match1_sp_value: float
    match1_european_odd: float
    match2_id: int
    match2_home_team: str
    match2_away_team: str
    match2_start_time: datetime
    match2_sp_value: float
    match2_european_odd: float
    total_sp_odd: float
    total_european_odd: float
    investment_amount: float
    revenue_amount: float
    profit_amount: float
    profit_rate: float
    is_profitable: bool


class HedgingOpportunityCreate(HedgingOpportunityBase):
    pass


class HedgingOpportunity(HedgingOpportunityBase):
    id: int
    date: datetime

    class Config:
        from_attributes = True


class HedgingConfigBase(BaseModel):
    min_profit_rate: float = 0.02
    commission_rate: float = 0.8
    cost_factor: float = 0.2


class HedgingConfigCreate(HedgingConfigBase):
    pass


class HedgingConfig(HedgingConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ParlayCombination(BaseModel):
    """二串一组合数据模型"""
    match1_id: int
    match1_home_team: str
    match1_away_team: str
    match1_start_time: datetime
    match1_sp_value: float
    match1_european_odd: float
    match2_id: int
    match2_home_team: str
    match2_away_team: str
    match2_start_time: datetime
    match2_sp_value: float
    match2_european_odd: float
    total_sp_odd: float
    total_european_odd: float
    investment_amount: float
    revenue_amount: float
    profit_amount: float
    profit_rate: float
    is_profitable: bool


class HedgingResult(BaseModel):
    """对冲结果模型"""
    date: str
    opportunities: List[ParlayCombination]
    total_count: int