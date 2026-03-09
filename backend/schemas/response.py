"""
统一响应模型
"""
from typing import Generic, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

T = TypeVar('T')


class UnifiedResponse(BaseModel, Generic[T]):
    """
    统一响应格式
    """
    code: int = 200
    message: str = "Success"
    data: Optional[T] = None
    timestamp: datetime = datetime.now()
    request_id: Optional[str] = None


class PageResponse(BaseModel, Generic[T]):
    """
    分页响应格式
    """
    code: int = 200
    message: str = "Success"
    data: List[T]
    total: int
    page: int
    size: int
    pages: int
    timestamp: datetime = datetime.now()


class ErrorResponse(BaseModel):
    """
    错误响应格式
    """
    code: int
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()