"""
爬虫告警规则模型
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func

from .base import Base


class CrawlerAlertRule(Base):
    """爬虫告警规则表"""
    __tablename__ = "crawler_alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    metric_type = Column(String(50), nullable=False, index=True)  # error_rate, response_time, consecutive_failures, data_quality
    threshold = Column(Float, nullable=False)
    comparison_operator = Column(String(10), nullable=False, index=True)  # gt, lt, eq, gte, lte
    time_window_minutes = Column(Integer, nullable=False, default=60)
    source_ids = Column(JSON, nullable=True)  # 指定数据源ID列表，null表示所有源
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    alert_level = Column(String(20), nullable=False, default='warning', index=True)  # warning, error, critical
    cooldown_minutes = Column(Integer, nullable=False, default=30)  # 告警冷却时间
    notification_channels = Column(JSON, nullable=False, default=['email'])  # 通知渠道
    created_by = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = {'extend_existing': True}
    
    def __repr__(self):
        return f"<CrawlerAlertRule(id={self.id}, name={self.name}, metric_type={self.metric_type})>"