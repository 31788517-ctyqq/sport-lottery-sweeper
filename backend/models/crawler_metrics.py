"""
爬虫监控指标模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func

from .base import Base


class CrawlerMetric(Base):
    """爬虫监控指标表"""
    __tablename__ = "crawler_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("crawler_configs.id"), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False, index=True)  # error_rate, response_time, request_count, etc.
    metric_value = Column(Float, nullable=False)
    tags = Column(JSON, nullable=True)
    recorded_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    
    __table_args__ = {'extend_existing': True}
    
    def __repr__(self):
        return f"<CrawlerMetric(id={self.id}, source_id={self.source_id}, metric_type={self.metric_type})>"