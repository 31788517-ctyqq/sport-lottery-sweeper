from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.database_async import get_async_db
from backend.schemas.role import (
    Role,
    RoleCreate,
    RoleUpdate,
    RoleWithPermissions
)
from backend.crud.role import crud_role

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=dict)
async def get_roles(
    db: AsyncSession = Depends(get_async_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    search: Optional[str] = None
):
    """
    获取角色列表
    """
    roles, total = await crud_role.get_multi_with_filter(
        db, skip=skip, limit=limit, status=status, search=search
    )
    return {
        "data": roles,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/options", response_model=List[dict])
async def get_role_options(
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取角色选项（扁平结构），用于下拉选择
    """
    roles, _ = await crud_role.get_multi_with_filter(db)
    options = [{"id": r.id, "label": r.name, "value": r.id} for r in roles]
    return options


@router.get("/stats", response_model=dict)
async def get_role_stats(
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取角色统计信息
    """
    roles, total = await crud_role.get_multi_with_filter(db)

    stats = {
        "total_roles": total,
        "active_roles": sum(1 for r in roles if r.status),
        "inactive_roles": sum(1 for r in roles if not r.status)
    }

    return stats


@router.get("/{id}", response_model=RoleWithPermissions)
async def get_role(
    *,
    id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取单个角色信息
    """
    role = await crud_role.get(db, id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.post("/", response_model=Role)
async def create_role(
    *,
    role_in: RoleCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    创建角色
    """
    existing_role = await crud_role.get_by_name(db, name=role_in.name)
    if existing_role:
        raise HTTPException(status_code=400, detail="Role name already exists")

    role = await crud_role.create(db, obj_in=role_in)
    return role


@router.put("/{id}", response_model=Role)
async def update_role(
    *,
    id: int,
    role_in: RoleUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    更新角色信息
    """
    role = await crud_role.get(db, id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    if role_in.name and role_in.name != role.name:
        existing_role = await crud_role.get_by_name(db, name=role_in.name)
        if existing_role and existing_role.id != id:
            raise HTTPException(status_code=400, detail="Role name already exists")

    role = await crud_role.update(db, db_obj=role, obj_in=role_in)
    return role


@router.delete("/{id}")
async def delete_role(
    *,
    id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """
    删除角色
    """
    role = await crud_role.get(db, id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # 检查角色是否被用户使用
    user_count = await crud_role.count_users(db, role_id=id)
    if user_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete role with assigned users")

    await crud_role.remove(db, id=id)
    return {"msg": "Role deleted successfully"}


@router.patch("/{id}/status")
async def update_role_status(
    *,
    id: int,
    status: str,
    db: AsyncSession = Depends(get_async_db)
):
    """
    更新角色状态
    """
    role = await crud_role.get(db, id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    role = await crud_role.update_status(db, role_id=id, status=status)
    return {"msg": f"Role status updated to {status}"}


@router.get("/{id}/permissions", response_model=List[int])
async def get_role_permissions(
    *,
    id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取角色的权限列表
    """
    role = await crud_role.get(db, id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # 返回角色拥有的权限ID列表
    permission_ids = [perm.id for perm in role.permissions] if role.permissions else []
    return permission_ids


@router.post("/{id}/permissions")
async def assign_role_permissions(
    *,
    id: int,
    permission_ids: List[int],
    db: AsyncSession = Depends(get_async_db)
):
    """
    为角色分配权限
    """
    role = await crud_role.get(db, id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # 更新角色权限
    updated_role = await crud_role.assign_permissions(db, role=role, permission_ids=permission_ids)
    return {"msg": "Permissions assigned successfully", "role_id": id, "permission_ids": permission_ids}
