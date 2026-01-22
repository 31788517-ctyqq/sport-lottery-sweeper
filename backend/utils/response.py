"""
统一响应格式
"""
from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel

T = TypeVar('T')

class UnifiedResponse(BaseModel, Generic[T]):
    """统一响应格式"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None
    
    @classmethod
    def success(cls, data: T = None, message: str = "success") -> "UnifiedResponse[T]":
        return cls(code=200, message=message, data=data)
    
    @classmethod
    def error(cls, code: int = 400, message: str = "error", data: T = None) -> "UnifiedResponse[T]":
        return cls(code=code, message=message, data=data)