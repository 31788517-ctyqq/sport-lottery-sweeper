"""
IP池模型
定义IP池的数据结构
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from .base import Base


class IPPool(Base):
    """IP池表"""
    __tablename__ = "ip_pools"
    
    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String(45), nullable=False, index=True)  # 支持IPv6
    port = Column(Integer, nullable=False)
    protocol = Column(String(10), nullable=False, default="http")  # http, https, socks5
    location = Column(String(100), nullable=True)  # IP地理位置
    # active/inactive/pending/testing/cooling/banned
    status = Column(String(20), nullable=False, default="active", index=True)
    remarks = Column(Text, nullable=True)  # 备注
    success_count = Column(Integer, nullable=False, default=0)  # 成功次数
    failure_count = Column(Integer, nullable=False, default=0)  # 失败次数
    last_used = Column(DateTime, nullable=True)  # 最后使用时间
    # 新增指标字段
    latency_ms = Column(Integer, nullable=True)  # 响应时间(ms)
    success_rate = Column(Integer, nullable=True)  # 0-100
    last_checked = Column(DateTime, nullable=True)  # 最近验证时间
    source = Column(String(100), nullable=True)  # IP来源
    anonymity = Column(String(50), nullable=True)  # 匿名级别
    score = Column(Integer, nullable=True)  # 综合得分
    banned_until = Column(DateTime, nullable=True)  # 封禁截至时间
    fail_reason = Column(Text, nullable=True)  # 最近失败原因
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "ip": self.ip,
            "port": self.port,
            "protocol": self.protocol,
            "location": self.location,
            "status": self.status,
            "remarks": self.remarks,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "latency_ms": self.latency_ms,
            "success_rate": self.success_rate,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
            "source": self.source,
            "anonymity": self.anonymity,
            "score": self.score,
            "banned_until": self.banned_until.isoformat() if self.banned_until else None,
            "fail_reason": self.fail_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
