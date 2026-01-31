#!/usr/bin/env python3
"""
通用 Pydantic Schema 定义
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    timestamp: datetime
    version: str
    uptime: Optional[float] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-25T10:30:00Z",
                "version": "1.0.0",
                "uptime": 3600.0
            }
        }
    )

class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: bool = True
    message: str
    code: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": True,
                "message": "参数验证失败",
                "code": 400,
                "details": {
                    "field": "username",
                    "reason": "用户名已存在"
                }
            }
        }
    )

class PaginationParams(BaseModel):
    """分页参数模型"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "page": 1,
                "size": 20
            }
        }
    )

# 导出所有schema
__all__ = ['HealthResponse', 'ErrorResponse', 'PaginationParams']