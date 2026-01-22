"""
系统配置相关Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SystemConfigBase(BaseModel):
    config_key: str
    config_value: str
    description: Optional[str] = None
    config_type: Optional[str] = "string"
    is_public: Optional[bool] = False


class SystemConfigCreate(SystemConfigBase):
    pass


class SystemConfigUpdate(BaseModel):
    config_value: Optional[str] = None
    description: Optional[str] = None
    config_type: Optional[str] = None
    is_public: Optional[bool] = None


class SystemConfig(SystemConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True