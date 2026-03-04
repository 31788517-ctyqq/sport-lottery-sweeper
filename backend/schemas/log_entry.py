"""
日志条目Schema
定义日志数据的输入输出格式
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class LogEntryBase(BaseModel):
    """日志条目基础模型"""
    timestamp: datetime
    level: str
    module: str
    message: str
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    request_path: Optional[str] = None
    response_status: Optional[int] = None
    duration_ms: Optional[int] = None
    extra_data: Optional[str] = None


class LogEntryCreate(LogEntryBase):
    """创建日志条目所需的数据"""
    pass


class LogEntryUpdate(BaseModel):
    """更新日志条目所需的数据"""
    level: Optional[str] = None
    module: Optional[str] = None
    message: Optional[str] = None
    extra_data: Optional[str] = None


class LogEntryInDBBase(LogEntryBase):
    """数据库中的日志条目基础模型"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LogEntry(LogEntryInDBBase):
    """日志条目响应模型"""
    pass


class LogEntryWithCount(BaseModel):
    """带总数的日志条目响应模型"""
    items: list[LogEntry]
    total: int