"""
数据源请求头绑定表模型
"""
from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from .base import Base


class DataSourceHeader(Base):
    """数据源与请求头绑定关系"""
    __tablename__ = "data_source_headers"

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id", ondelete="CASCADE"), nullable=False)
    header_id = Column(Integer, ForeignKey("request_headers.id", ondelete="CASCADE"), nullable=False)
    priority_override = Column(Integer, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("data_source_id", "header_id", name="uq_data_source_header"),
    )
