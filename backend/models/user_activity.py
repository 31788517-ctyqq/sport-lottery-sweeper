"""
用户活动日志模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class UserActivity(Base):
    """用户活动日志"""
    __tablename__ = 'user_activities'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    activity_type = Column(String(100), nullable=False)
    activity_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    description = Column(Text, nullable=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(50), nullable=True)
    resource_name = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    endpoint = Column(String(255), nullable=True)
    http_method = Column(String(10), nullable=True)
    http_status = Column(Integer, nullable=True)
    details = Column(Text, nullable=False, default="")
    
    # 关系
    user = relationship("User", back_populates="activities")