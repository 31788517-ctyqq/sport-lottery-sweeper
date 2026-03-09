"""
日志条目模型
用于存储系统日志、用户日志、安全日志等
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.sql import func
from .base import Base


class LogEntry(Base):
    """日志条目模型"""
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now(), index=True)
    level = Column(String(20), index=True)  # DEBUG, INFO, WARN, ERROR, CRITICAL
    module = Column(String(100), index=True)  # 模块名称
    message = Column(Text)  # 日志消息
    user_id = Column(Integer, index=True, nullable=True)  # 用户ID（如果是用户操作日志）
    ip_address = Column(String(45), index=True, nullable=True)  # IP地址
    user_agent = Column(Text, nullable=True)  # 用户代理
    session_id = Column(String(100), index=True, nullable=True)  # 会话ID
    request_path = Column(String(500), nullable=True)  # 请求路径
    response_status = Column(Integer, nullable=True)  # 响应状态码
    duration_ms = Column(Integer, nullable=True)  # 请求持续时间（毫秒）
    extra_data = Column(Text, nullable=True)  # 额外的JSON数据
    created_at = Column(DateTime, default=func.now())

    # 为常用查询创建复合索引
    __table_args__ = (
        Index('idx_timestamp_level', 'timestamp', 'level'),
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_module_level', 'module', 'level'),
    )

    def __repr__(self):
        return f"<LogEntry(id={self.id}, timestamp={self.timestamp}, level='{self.level}', module='{self.module}', message='{self.message[:50]}...')>"