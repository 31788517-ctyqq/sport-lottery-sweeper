"""
爬虫任务请求头绑定表模型
"""
from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from .base import Base


class CrawlerTaskHeader(Base):
    """任务与请求头绑定关系"""
    __tablename__ = "crawler_task_headers"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("crawler_tasks.id", ondelete="CASCADE"), nullable=False)
    header_id = Column(Integer, ForeignKey("request_headers.id", ondelete="CASCADE"), nullable=False)
    priority_override = Column(Integer, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("task_id", "header_id", name="uq_task_header"),
    )
