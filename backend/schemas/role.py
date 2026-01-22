"""
角色和权限相关的Pydantic模型
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RoleBase(BaseModel):
    """角色基础模型"""
    name: str
    description: Optional[str] = None
    permissions: Optional[list] = []


class RoleCreate(RoleBase):
    """创建角色请求模型"""
    name: str
    description: Optional[str] = None
    permissions: Optional[list] = []


class RoleUpdate(BaseModel):
    """更新角色请求模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[list] = None


class RoleResponse(RoleBase):
    """角色响应模型"""
    id: int
    name: str
    description: Optional[str]
    permissions: list
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PermissionBase(BaseModel):
    """权限基础模型"""
    name: str
    description: Optional[str] = None
    resource: str
    action: str


class PermissionCreate(PermissionBase):
    """创建权限请求模型"""
    pass


class PermissionUpdate(BaseModel):
    """更新权限请求模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None


class PermissionResponse(PermissionBase):
    """权限响应模型"""
    id: int
    name: str
    description: Optional[str]
    resource: str
    action: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True