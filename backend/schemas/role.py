"""
角色和权限相关的Pydantic模型
"""
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import json


class RoleLevelEnum(str, Enum):
    """角色等级枚举"""
    SUPER_ADMIN = "5"   # 超级管理员
    ADMIN = "4"         # 管理员
    AUDITOR = "3"       # 审计员
    OPERATOR = "2"      # 运营员
    OBSERVER = "1"      # 观察者


ROLE_LEVEL_NAMES = {
    "5": "超级管理员 (L5)",
    "4": "管理员 (L4)",
    "3": "审计员 (L3)",
    "2": "运营员 (L2)",
    "1": "观察者 (L1)",
}


class RoleBase(BaseModel):
    """角色基础模型"""
    name: str
    description: Optional[str] = None
    level: int = 1
    is_system: bool = False
    permissions: Optional[list] = []

    @validator('permissions', pre=True)
    def parse_permissions(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return parsed if isinstance(parsed, list) else []
            except Exception:
                return []
        return value


class RoleCreate(RoleBase):
    """创建角色请求模型"""
    name: str
    description: Optional[str] = None
    level: int = 1
    is_system: bool = False
    permissions: Optional[list] = []


class RoleUpdate(BaseModel):
    """更新角色请求模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None
    is_system: Optional[bool] = None
    permissions: Optional[list] = None

    @validator('permissions', pre=True)
    def parse_permissions(cls, value):
        if value is None:
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return parsed if isinstance(parsed, list) else []
            except Exception:
                return []
        return value


class RoleResponse(RoleBase):
    """角色响应模型"""
    id: int
    name: str
    description: Optional[str]
    level: int
    is_system: bool
    permissions: list
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 兼容现有导入
Role = RoleResponse


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


# 角色及权限详情响应模型（放在 PermissionResponse 之后）
class RoleWithPermissions(RoleResponse):
    """角色及权限详情响应模型"""
    permissions_detail: List[PermissionResponse] = []

    class Config:
        from_attributes = True