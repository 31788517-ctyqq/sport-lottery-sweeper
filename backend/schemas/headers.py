"""
请求头Schema
定义请求头相关的数据验证模式
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RequestHeaderBase(BaseModel):
    domain: str
    name: str
    value: str
    type: str = "general"
    priority: int = 1
    status: str = "enabled"
    remarks: Optional[str] = None


class RequestHeaderCreate(RequestHeaderBase):
    pass


class RequestHeaderUpdate(BaseModel):
    domain: Optional[str] = None
    name: Optional[str] = None
    value: Optional[str] = None
    type: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    remarks: Optional[str] = None


class RequestHeaderResponse(RequestHeaderBase):
    id: int
    usage_count: int = 0
    success_count: int = 0
    last_used: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    success_rate: Optional[float] = None

    class Config:
        from_attributes = True