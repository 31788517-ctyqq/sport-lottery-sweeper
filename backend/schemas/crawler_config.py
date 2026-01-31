"""
爬虫配置相关Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CrawlerConfigBase(BaseModel):
    name: str
    source_url: str
    enabled: Optional[bool] = True
    interval_minutes: Optional[int] = 60
    timeout_seconds: Optional[int] = 30
    retry_times: Optional[int] = 3
    headers: Optional[str] = None
    proxy_enabled: Optional[bool] = False
    priority: Optional[int] = 1


class CrawlerConfigCreate(CrawlerConfigBase):
    pass


class CrawlerConfigUpdate(BaseModel):
    source_url: Optional[str] = None
    enabled: Optional[bool] = None
    interval_minutes: Optional[int] = None
    timeout_seconds: Optional[int] = None
    retry_times: Optional[int] = None
    headers: Optional[str] = None
    proxy_enabled: Optional[bool] = None
    priority: Optional[int] = None


class CrawlerConfig(CrawlerConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CrawlerConfigResponse(BaseModel):
    """爬虫配置响应模型"""
    id: int
    name: str
    source_url: str
    enabled: bool
    interval_minutes: int
    timeout_seconds: int
    retry_times: int
    headers: Optional[str]
    proxy_enabled: bool
    priority: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True