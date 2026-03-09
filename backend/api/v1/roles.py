import json
import logging
from typing import Any, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.database_async import get_async_db
from backend.schemas.role import (
    Role,
    RoleCreate,
    RoleUpdate,
    RoleWithPermissions
)
from backend.crud.role import crud_role

router = APIRouter(prefix="/roles", tags=["roles"])
_roles_schema_checked = False
logger = logging.getLogger(__name__)


async def _ensure_roles_schema(db: AsyncSession) -> None:
    """Best-effort compatibility patch for legacy roles table schema."""
    global _roles_schema_checked
    if _roles_schema_checked:
        return

    statements = [
        "ALTER TABLE roles ADD COLUMN IF NOT EXISTS level INTEGER DEFAULT 1",
        "ALTER TABLE roles ADD COLUMN IF NOT EXISTS is_system BOOLEAN DEFAULT FALSE",
        "ALTER TABLE roles ADD COLUMN IF NOT EXISTS sort_order INTEGER DEFAULT 0",
    ]
    try:
        for statement in statements:
            await db.execute(text(statement))
        await db.commit()
        _roles_schema_checked = True
    except Exception:
        await db.rollback()
        logger.warning("roles schema compatibility patch failed", exc_info=True)


def _parse_permission_ids(raw_permissions: Any) -> List[int]:
    """Normalize role permission payload from DB JSON/text/list to integer ID list."""
    if raw_permissions is None:
        return []
    if isinstance(raw_permissions, list):
        values = raw_permissions
    elif isinstance(raw_permissions, str):
        try:
            parsed = json.loads(raw_permissions)
            values = parsed if isinstance(parsed, list) else []
        except Exception:
            return []
    else:
        return []

    normalized: List[int] = []
    for item in values:
        try:
            normalized.append(int(item))
        except Exception:
            continue
    return normalized


def _serialize_role(role_obj) -> dict:
    return {
        "id": role_obj.id,
        "name": role_obj.name,
        "description": role_obj.description,
        "level": getattr(role_obj, "level", 1),
        "is_system": getattr(role_obj, "is_system", False),
        "status": role_obj.status,
        "permissions": _parse_permission_ids(role_obj.permissions),
        "created_at": role_obj.created_at,
        "updated_at": role_obj.updated_at,
    }


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
    await _ensure_roles_schema(db)
    roles, total = await crud_role.get_multi_with_filter(
        db, skip=skip, limit=limit, status=status, search=search
    )

    return {
        "data": [_serialize_role(role) for role in roles],
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
    await _ensure_roles_schema(db)
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
    await _ensure_roles_schema(db)
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
    await _ensure_roles_schema(db)
    role = await crud_role.get(db, role_id=id)
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
    await _ensure_roles_schema(db)
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
    await _ensure_roles_schema(db)
    role = await crud_role.get(db, role_id=id)
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
    await _ensure_roles_schema(db)
    role = await crud_role.get(db, role_id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # 检查角色是否被用户使用
    user_count = await crud_role.count_users(db, role_id=id, role_name=role.name)
    if user_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete role with assigned users")

    await crud_role.remove(db, role_id=id)
    return {"msg": "Role deleted successfully"}


@router.patch("/{id}/status")
async def update_role_status(
    *,
    id: int,
    status: Optional[str] = None,
    payload: Optional[dict] = Body(default=None),
    db: AsyncSession = Depends(get_async_db)
):
    """
    更新角色状态
    """
    await _ensure_roles_schema(db)
    final_status = status
    if final_status is None and isinstance(payload, dict):
        final_status = payload.get("status")
    if final_status is None:
        raise HTTPException(status_code=422, detail="status is required")

    role = await crud_role.get(db, role_id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    try:
        role = await crud_role.update_status(db, role_id=id, status=final_status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"msg": f"Role status updated to {final_status}"}


@router.get("/{id}/permissions", response_model=List[int])
async def get_role_permissions(
    *,
    id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取角色的权限列表
    """
    await _ensure_roles_schema(db)
    role = await crud_role.get(db, role_id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # 返回角色拥有的权限ID列表（permissions字段存储为JSON文本）
    permission_ids = _parse_permission_ids(role.permissions)
    return permission_ids


@router.post("/{id}/permissions")
async def assign_role_permissions(
    *,
    id: int,
    permission_ids: Any = Body(...),
    db: AsyncSession = Depends(get_async_db)
):
    """
    为角色分配权限
    """
    await _ensure_roles_schema(db)
    role = await crud_role.get(db, role_id=id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    raw_ids = permission_ids
    if isinstance(permission_ids, dict):
        raw_ids = (
            permission_ids.get("permission_ids")
            or permission_ids.get("permissionIds")
            or permission_ids.get("permissions")
            or []
        )
    normalized_ids = _parse_permission_ids(raw_ids)

    # 更新角色权限
    await crud_role.assign_permissions(db, role=role, permission_ids=normalized_ids)
    return {"msg": "Permissions assigned successfully", "role_id": id, "permission_ids": normalized_ids}
