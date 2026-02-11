"""
爬虫任务模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

from .base import Base
from ..config import settings


class CrawlerTask(Base):
    """爬虫任务表"""
    __tablename__ = "crawler_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    source_id = Column(Integer, ForeignKey("data_sources.id", ondelete="CASCADE"), nullable=False)
    task_type = Column(String(50), nullable=False, default='crawl')
    cron_expression = Column(String(100), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    status = Column(String(20), nullable=False, default='stopped')  # stopped, running, paused
    last_run_time = Column(DateTime, nullable=True)
    next_run_time = Column(DateTime, nullable=True)
    run_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)
    config = Column(JSON, nullable=True)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 索引已在迁移文件中创建
    
    __table_args__ = (
        {'sqlite_autoincrement': True} if 'sqlite' in settings.DATABASE_URL else {}
    )