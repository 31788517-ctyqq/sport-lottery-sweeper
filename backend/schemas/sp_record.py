"""
SP值记录相关Schema定义
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class SPRecordBase(BaseModel):
    match_id: int = Field(..., description="比赛ID")
    company_id: int = Field(..., description="公司ID")
    handicap_type: str = Field(..., max_length=20, description="盘口类型: handicap/no_handicap")
    handicap_value: Optional[Decimal] = Field(None, description="让球数值")
    sp_value: Decimal = Field(..., description="SP值")
    recorded_at: datetime = Field(..., description="记录时间")


class SPRecordCreate(SPRecordBase):
    pass


class SPRecordUpdate(BaseModel):
    sp_value: Optional[Decimal] = None
    reason: Optional[str] = Field(None, description="修改原因")


class SPRecordResponse(SPRecordBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SPRecordListResponse(BaseModel):
    items: List[SPRecordResponse]
    total: int
    page: int
    size: int


class SPModifyRequest(BaseModel):
    sp_value: Decimal = Field(..., description="新的SP值")
    reason: Optional[str] = Field(None, max_length=500, description="修改原因")