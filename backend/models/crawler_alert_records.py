"""
爬虫告警记录模型
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base


class CrawlerAlertRecord(Base):
    """爬虫告警记录表"""
    __tablename__ = "crawler_alert_records"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("crawler_alert_rules.id"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("crawler_configs.id"), nullable=True, index=True)
    alert_level = Column(String(20), nullable=False, index=True)  # warning, error, critical
    metric_value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, default='active', index=True)  # active, resolved, acknowledged
    triggered_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    resolved_at = Column(DateTime, nullable=True, index=True)
    acknowledged_by = Column(Integer, nullable=True, index=True)
    acknowledged_at = Column(DateTime, nullable=True, index=True)
    
    # 关系
    rule = relationship("CrawlerAlertRule", backref="alert_records")
    source = relationship("CrawlerConfig", backref="alert_records")
    
    __table_args__ = {'extend_existing': True}
    
    def __repr__(self):
        return f"<CrawlerAlertRecord(id={self.id}, rule_id={self.rule_id}, alert_level={self.alert_level})>"