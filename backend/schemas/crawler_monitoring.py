"""
爬虫监控相关Schema定义
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class MonitoringOverview(BaseModel):
    """监控概览数据"""
    total_sources: int
    active_sources: int
    total_alerts: int
    active_alerts: int
    success_rate: float
    avg_response_time: float
    uptime: float
    last_updated: datetime

    class Config:
        from_attributes = True


class SourcePerformance(BaseModel):
    """数据源性能数据"""
    source_id: int
    source_name: str
    success_rate: float
    avg_response_time: float
    total_requests: int
    successful_requests: int
    error_rate: float
    last_checked: datetime
    status: str

    class Config:
        from_attributes = True


class AlertTrends(BaseModel):
    """告警趋势数据"""
    alert_type: str
    count: int
    trend: str  # up, down, stable
    change_percentage: float
    last_24h: int
    last_7d: int

    class Config:
        from_attributes = True


class RealtimeMetrics(BaseModel):
    """实时指标数据"""
    timestamp: datetime
    active_crawlers: int
    queued_tasks: int
    processing_tasks: int
    completed_tasks: int
    error_tasks: int
    avg_processing_time: float

    class Config:
        from_attributes = True


class TopIssues(BaseModel):
    """主要问题数据"""
    issue_type: str
    count: int
    severity: str  # high, medium, low
    affected_sources: List[str]
    first_occurred: datetime
    last_occurred: datetime

    class Config:
        from_attributes = True