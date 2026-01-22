"""
数据源相关Schema定义
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DataSourceBase(BaseModel):
    name: str = Field(..., max_length=100, description="数据源名称")
    type: str = Field(..., max_length=20, description="类型: api/file")
    status: Optional[bool] = Field(True, description="启用状态")
    url: Optional[str] = Field(None, max_length=500, description="接口地址或文件路径")
    config: Optional[str] = Field(None, description="配置信息(JSON格式)")
    last_update: Optional[datetime] = Field(None, description="最后更新时间")
    error_rate: Optional[float] = Field(0, description="错误率")


class DataSourceCreate(DataSourceBase):
    pass


class DataSourceUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    type: Optional[str] = Field(None, max_length=20)
    status: Optional[bool] = None
    url: Optional[str] = Field(None, max_length=500)
    config: Optional[str] = None
    last_update: Optional[datetime] = None
    error_rate: Optional[float] = None


class DataSourceResponse(DataSourceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True