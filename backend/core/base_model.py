from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from backend.models.base import Base


class BaseFullModel(Base):
    """基础模型类，包含通用字段"""
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, index=True)