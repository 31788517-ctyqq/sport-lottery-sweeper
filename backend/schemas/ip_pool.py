"""
IP池Schema
定义IP池相关的数据验证模式
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class IPPoolBase(BaseModel):
    ip: str
    port: int
    protocol: str = "http"
    location: Optional[str] = None
    status: str = "active"
    remarks: Optional[str] = None
    latency_ms: Optional[int] = None
    success_rate: Optional[int] = None
    last_checked: Optional[datetime] = None
    source: Optional[str] = None
    anonymity: Optional[str] = None
    score: Optional[int] = None
    banned_until: Optional[datetime] = None
    fail_reason: Optional[str] = None


class IPPoolCreate(IPPoolBase):
    pass


class IPPoolUpdate(BaseModel):
    ip: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    remarks: Optional[str] = None
    latency_ms: Optional[int] = None
    success_rate: Optional[int] = None
    last_checked: Optional[datetime] = None
    source: Optional[str] = None
    anonymity: Optional[str] = None
    score: Optional[int] = None
    banned_until: Optional[datetime] = None
    fail_reason: Optional[str] = None


class IPPoolResponse(IPPoolBase):
    id: int
    success_count: int = 0
    failure_count: int = 0
    last_used: Optional[datetime] = None
    latency_ms: Optional[int] = None
    success_rate: Optional[int] = None
    last_checked: Optional[datetime] = None
    source: Optional[str] = None
    anonymity: Optional[str] = None
    score: Optional[int] = None
    banned_until: Optional[datetime] = None
    fail_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
