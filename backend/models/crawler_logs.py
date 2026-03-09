"""
爬虫日志和统计模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON, Date, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

from .base import Base


class CrawlerTaskLog(Base):
    """爬虫任务执行日志"""
    __tablename__ = "crawler_task_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("crawler_tasks.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(Integer, ForeignKey("crawler_configs.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False)  # running, success, failed, timeout
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    records_processed = Column(Integer, nullable=True, default=0)
    records_success = Column(Integer, nullable=True, default=0)
    records_failed = Column(Integer, nullable=True, default=0)
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    response_time_ms = Column(Float, nullable=True)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # 索引已在迁移文件中创建
    
    __table_args__ = {
        'extend_existing': True,
        'sqlite_autoincrement': True
    }


class CrawlerSourceStat(Base):
    """数据源统计"""
    __tablename__ = "crawler_source_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("crawler_configs.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    total_requests = Column(Integer, nullable=False, default=0)
    successful_requests = Column(Integer, nullable=False, default=0)
    failed_requests = Column(Integer, nullable=False, default=0)
    avg_response_time_ms = Column(Float, nullable=True)
    total_records = Column(Integer, nullable=False, default=0)
    last_success_at = Column(DateTime, nullable=True)
    last_failure_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 复合唯一约束和索引已在迁移文件中创建
    
    __table_args__ = {
        'sqlite_autoincrement': True
    }