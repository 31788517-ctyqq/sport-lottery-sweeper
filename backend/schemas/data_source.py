"""
数据源相关Schema定义
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime
from .data_source_types import DataSourceType, create_data_source_config, get_data_source_type_description


class DataSourceBase(BaseModel):
    name: str = Field(..., max_length=100, description="数据源名称")
    type: DataSourceType = Field(..., description="数据源类型")
    status: Optional[str] = Field('online', description="状态: online/offline/maintenance/error")  # 修改为字符串类型
    url: Optional[str] = Field(None, max_length=500, description="接口地址或文件路径")
    config: Optional[str] = Field(None, description="配置信息(JSON格式)")
    last_update: Optional[datetime] = Field(None, description="最后更新时间")
    error_rate: Optional[float] = Field(0, description="错误率")
    
    class Config:
        use_enum_values = True


class DataSourceCreate(DataSourceBase):
    pass


class DataSourceUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    type: Optional[str] = Field(None, max_length=20)  # 修改为字符串类型
    status: Optional[str] = None  # 修改为字符串类型
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