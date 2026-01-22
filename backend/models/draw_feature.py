from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from datetime import datetime
from .base import Base

class DrawFeature(Base):
    __tablename__ = "draw_features"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False, comment="特征名称")
    description = Column(Text, comment="特征描述")
    source_type = Column(String(64), nullable=False, comment="数据来源类型")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    meta = Column(JSON, comment="额外元数据")
