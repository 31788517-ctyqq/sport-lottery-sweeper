"""
智能分析记录相关Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class IntelligenceRecordBase(BaseModel):
    analysis_type: str
    target_data: Optional[str] = None
    result_summary: Optional[str] = None
    confidence_score: Optional[float] = None
    model_used: Optional[str] = None
    processing_time_ms: Optional[int] = None
    status: Optional[str] = "completed"


class IntelligenceRecordCreate(IntelligenceRecordBase):
    pass


class IntelligenceRecordUpdate(BaseModel):
    result_summary: Optional[str] = None
    confidence_score: Optional[float] = None
    model_used: Optional[str] = None
    processing_time_ms: Optional[int] = None
    status: Optional[str] = None


class IntelligenceRecord(IntelligenceRecordBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True