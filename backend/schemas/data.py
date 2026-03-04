"""
数据管理相关Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AdminDataBase(BaseModel):
    title: str
    content: str
    category: str
    tags: Optional[str] = None
    status: Optional[str] = "active"
    sort_order: Optional[int] = 0


class AdminDataCreate(AdminDataBase):
    pass


class AdminDataUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    status: Optional[str] = None
    sort_order: Optional[int] = None


class AdminData(AdminDataBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True