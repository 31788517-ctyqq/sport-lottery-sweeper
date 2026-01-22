"""
赔率公司相关Schema定义
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CompanyBase(BaseModel):
    name: str = Field(..., max_length=100, description="公司名称")
    short_name: Optional[str] = Field(None, max_length=20, description="简称")
    logo_url: Optional[str] = Field(None, max_length=200, description="Logo地址")
    status: Optional[bool] = Field(True, description="启用状态")
    weight: Optional[float] = Field(1.0, description="权重/优先级")


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    short_name: Optional[str] = Field(None, max_length=20)
    logo_url: Optional[str] = Field(None, max_length=200)
    status: Optional[bool] = None
    weight: Optional[float] = None


class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True