#!/usr/bin/env python3
"""
核心响应模块 - 兼容层
提供统一的API响应格式，兼容旧的导入路径
"""

from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel

def success_response(data: Any = None, message: str = "Success", code: int = 200) -> dict:
    """
    成功响应格式（兼容旧版本）
    """
    return {
        "code": code,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

def error_response(message: str = "Error", code: int = 400, error_code: Optional[str] = None, details: Optional[dict] = None) -> dict:
    """
    错误响应格式（兼容旧版本）
    """
    return {
        "code": code,
        "message": message,
        "error_code": error_code,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }

# 为了兼容性，也从schemas导入现代响应类
from ..schemas.response import UnifiedResponse, PageResponse, ErrorResponse

# 兼容类 APIResponse（用于旧测试）
class APIResponse(BaseModel):
    """
    兼容旧版本的 APIResponse 类
    """
    code: int
    message: str
    data: Optional[Any] = None
    error_code: Optional[str] = None
    
    def to_dict(self) -> dict:
        """
        转换为字典格式
        """
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data,
            "error_code": self.error_code,
            "timestamp": datetime.now().isoformat()
        }

__all__ = [
    'success_response', 
    'error_response',
    'APIResponse',
    'UnifiedResponse',
    'PageResponse', 
    'ErrorResponse'
]