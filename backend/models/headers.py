"""
请求头模型
定义请求头的数据结构
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .base import Base


class RequestHeader(Base):
    """请求头表"""
    __tablename__ = "request_headers"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), nullable=False, index=True)  # 目标域名
    name = Column(String(255), nullable=False)  # 请求头名称
    value = Column(Text, nullable=False)  # 请求头值
    type = Column(String(50), nullable=False, default="general")  # general, request, response
    priority = Column(Integer, nullable=False, default=1)  # 优先级，数值越大优先级越高
    status = Column(String(20), nullable=False, default="enabled")  # enabled, disabled
    remarks = Column(Text, nullable=True)  # 备注
    usage_count = Column(Integer, nullable=False, default=0)  # 使用次数
    success_count = Column(Integer, nullable=False, default=0)  # 成功次数
    last_used = Column(DateTime, nullable=True)  # 最后使用时间
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "domain": self.domain,
            "name": self.name,
            "value": self.value,
            "type": self.type,
            "priority": self.priority,
            "status": self.status,
            "remarks": self.remarks,
            "usage_count": self.usage_count,
            "success_count": self.success_count,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "success_rate": round(self.success_count / self.usage_count * 100, 2) if self.usage_count > 0 else 100
        }