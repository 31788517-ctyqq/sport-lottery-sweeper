from fastapi import APIRouter, Depends
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database_async import get_async_db
from pydantic import BaseModel

router = APIRouter(prefix="/permissions", tags=["permissions"])

# Pydantic模型定义
class Permission(BaseModel):
    id: int
    name: str
    code: str
    description: str
    parentId: Optional[int] = None
    children: List['Permission'] = []

    class Config:
        from_attributes = True

# 模拟权限数据
PERMISSIONS_DATA = [
    {"id": 1, "name": "用户管理", "code": "user_management", "description": "管理用户账户", "parentId": None},
    {"id": 2, "name": "查看用户", "code": "user_view", "description": "查看用户信息", "parentId": 1},
    {"id": 3, "name": "创建用户", "code": "user_create", "description": "创建新用户", "parentId": 1},
    {"id": 4, "name": "编辑用户", "code": "user_edit", "description": "编辑用户信息", "parentId": 1},
    {"id": 5, "name": "删除用户", "code": "user_delete", "description": "删除用户", "parentId": 1},
    {"id": 6, "name": "角色管理", "code": "role_management", "description": "管理角色权限", "parentId": None},
    {"id": 7, "name": "查看角色", "code": "role_view", "description": "查看角色信息", "parentId": 6},
    {"id": 8, "name": "创建角色", "code": "role_create", "description": "创建新角色", "parentId": 6},
    {"id": 9, "name": "编辑角色", "code": "role_edit", "description": "编辑角色权限", "parentId": 6},
    {"id": 10, "name": "删除角色", "code": "role_delete", "description": "删除角色", "parentId": 6},
    {"id": 11, "name": "数据管理", "code": "data_management", "description": "管理数据", "parentId": None},
    {"id": 12, "name": "查看数据", "code": "data_view", "description": "查看数据", "parentId": 11},
    {"id": 13, "name": "编辑数据", "code": "data_edit", "description": "编辑数据", "parentId": 11},
    {"id": 14, "name": "系统设置", "code": "system_settings", "description": "管理系统设置", "parentId": None},
    {"id": 15, "name": "查看设置", "code": "settings_view", "description": "查看系统设置", "parentId": 14},
    {"id": 16, "name": "编辑设置", "code": "settings_edit", "description": "编辑系统设置", "parentId": 14},
]

@router.get("/", response_model=List[Permission])
async def get_permissions():
    """
    获取权限列表
    """
    # 将权限数据转换为树形结构
    permission_map = {perm["id"]: Permission(**perm, children=[]) for perm in PERMISSIONS_DATA}
    
    root_permissions = []
    for perm_data in PERMISSIONS_DATA:
        perm = permission_map[perm_data["id"]]
        if perm_data["parentId"] is None:
            root_permissions.append(perm)
        else:
            parent = permission_map.get(perm_data["parentId"])
            if parent:
                parent.children.append(perm)
    
    return root_permissions

@router.get("/tree", response_model=List[Permission])
async def get_permission_tree():
    """
    获取权限树形结构
    """
    # 与获取权限列表相同，因为已经是树形结构
    return await get_permissions()

@router.get("/flat", response_model=List[dict])
async def get_permissions_flat():
    """
    获取权限扁平列表
    """
    return PERMISSIONS_DATA