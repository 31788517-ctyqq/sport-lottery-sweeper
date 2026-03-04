"""
爬虫数据源统计模型
用于 EnhancedCrawlerService 的统计功能
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class CrawlerSourceStat(Base):
    """爬虫数据源统计表"""
    __tablename__ = "crawler_source_stats"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, nullable=False, comment="数据源ID")
    source_name = Column(String(255), comment="数据源名称")
    date = Column(Date, nullable=False, comment="统计日期")
    total_requests = Column(Integer, default=0, comment="总请求数")
    successful_requests = Column(Integer, default=0, comment="成功请求数")
    failed_requests = Column(Integer, default=0, comment="失败请求数")
    total_records = Column(Integer, default=0, comment="总记录数")
    avg_response_time_ms = Column(Float, comment="平均响应时间(毫秒)")
    last_success_at = Column(DateTime, comment="最后成功时间")
    last_failure_at = Column(DateTime, comment="最后失败时间")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CrawlerSourceStat(id={self.id}, source_id={self.source_id}, date={self.date})>"