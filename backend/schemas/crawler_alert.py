"""
爬虫告警相关的Schema模型
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class AlertRuleBase(BaseModel):
    """告警规则基础模型"""
    name: str = Field(..., description="规则名称")
    description: Optional[str] = Field(None, description="规则描述")
    metric_type: str = Field(..., description="指标类型: error_rate, response_time, consecutive_failures, data_quality")
    threshold: float = Field(..., description="告警阈值")
    comparison_operator: str = Field(..., description="比较操作符: gt, lt, eq, gte, lte")
    time_window_minutes: int = Field(60, description="时间窗口（分钟）")
    source_ids: Optional[List[int]] = Field(None, description="数据源ID列表，null表示所有源")
    is_active: bool = Field(True, description="是否激活")
    alert_level: str = Field("warning", description="告警级别: warning, error, critical")
    cooldown_minutes: int = Field(30, description="冷却时间（分钟）")
    notification_channels: List[str] = Field(["email"], description="通知渠道: email, slack, webhook")


class AlertRuleCreate(AlertRuleBase):
    """创建告警规则模型"""
    pass


class AlertRuleUpdate(BaseModel):
    """更新告警规则模型"""
    name: Optional[str] = Field(None, description="规则名称")
    description: Optional[str] = Field(None, description="规则描述")
    metric_type: Optional[str] = Field(None, description="指标类型")
    threshold: Optional[float] = Field(None, description="告警阈值")
    comparison_operator: Optional[str] = Field(None, description="比较操作符")
    time_window_minutes: Optional[int] = Field(None, description="时间窗口（分钟）")
    source_ids: Optional[List[int]] = Field(None, description="数据源ID列表")
    is_active: Optional[bool] = Field(None, description="是否激活")
    alert_level: Optional[str] = Field(None, description="告警级别")
    cooldown_minutes: Optional[int] = Field(None, description="冷却时间（分钟）")
    notification_channels: Optional[List[str]] = Field(None, description="通知渠道")


class AlertRuleResponse(AlertRuleBase):
    """告警规则响应模型"""
    id: int
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AlertRecordBase(BaseModel):
    """告警记录基础模型"""
    rule_id: int
    source_id: Optional[int] = None
    alert_level: str
    metric_value: float
    threshold: float
    message: str
    details: Optional[Dict[str, Any]] = None
    status: str = Field("active", description="状态: active, resolved, acknowledged")


class AlertRecordResponse(AlertRecordBase):
    """告警记录响应模型"""
    id: int
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AlertCheckResult(BaseModel):
    """告警检查结果模型"""
    success: bool
    message: str
    triggered_count: int
    alerts: List[Dict[str, Any]] = []


class MetricRecordRequest(BaseModel):
    """指标记录请求模型"""
    source_id: int
    metric_type: str
    metric_value: float
    tags: Optional[Dict[str, Any]] = None


class AlertStats(BaseModel):
    """告警统计模型"""
    total_alerts: int
    active_alerts: int
    resolved_alerts: int
    alerts_by_level: Dict[str, int]
    recent_alerts: List[AlertRecordResponse]
    top_failing_sources: List[Dict[str, Any]]