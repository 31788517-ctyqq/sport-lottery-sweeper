from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.crud.department import crud_department
from backend.database_async import get_async_db
from backend.models.admin_user import AdminUser
from backend.models.department import Department as DepartmentModel
from backend.schemas.admin_user import AdminUserResponse
from backend.schemas.department import DepartmentCreate, DepartmentUpdate

router = APIRouter(prefix="/departments", tags=["departments"])


class DepartmentStatusUpdateRequest(BaseModel):
    status: Any


class DepartmentMoveRequest(BaseModel):
    parent_id: Optional[int] = None


class DepartmentBatchDeleteRequest(BaseModel):
    ids: List[int]


class DepartmentMembersRequest(BaseModel):
    user_ids: Optional[List[int]] = None
    userIds: Optional[List[int]] = None

    def normalized_user_ids(self) -> List[int]:
        raw = self.user_ids if self.user_ids is not None else self.userIds
        if not raw:
            return []
        unique_ids: List[int] = []
        seen = set()
        for item in raw:
            try:
                uid = int(item)
            except (TypeError, ValueError):
                continue
            if uid not in seen:
                seen.add(uid)
                unique_ids.append(uid)
        return unique_ids


def _normalize_status(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"active", "1", "true", "enabled", "enable"}:
            return True
        if lowered in {"inactive", "0", "false", "disabled", "disable"}:
            return False
    raise HTTPException(status_code=422, detail="Invalid status value")


def _serialize_department(dept) -> Dict[str, Any]:
    return {
        "id": dept.id,
        "name": dept.name,
        "parent_id": dept.parent_id,
        "description": dept.description or "",
        "leader_id": dept.leader_id,
        "status": bool(dept.status),
        "sort_order": dept.sort_order or 0,
        "created_at": dept.created_at,
        "updated_at": dept.updated_at,
    }


def _serialize_department_tree_node(dept) -> Dict[str, Any]:
    node = _serialize_department(dept)
    children = getattr(dept, "children", None) or []
    node["children"] = [_serialize_department_tree_node(child) for child in children]
    return node


def _build_tree_from_departments(departments: List[DepartmentModel]) -> List[Dict[str, Any]]:
    nodes: Dict[int, Dict[str, Any]] = {}
    roots: List[Dict[str, Any]] = []

    for dept in departments:
        node = _serialize_department(dept)
        node["children"] = []
        nodes[dept.id] = node

    for dept in departments:
        node = nodes[dept.id]
        parent_id = dept.parent_id
        if parent_id and parent_id in nodes:
            nodes[parent_id]["children"].append(node)
        else:
            roots.append(node)

    return roots


@router.get("/", response_model=dict)
async def get_departments(
    db: AsyncSession = Depends(get_async_db),
    skip: int = 0,
    limit: int = 100,
    tree: bool = False,
    search: Optional[str] = None,
):
    """
    获取部门列表，支持树结构。
    """
    if tree:
        query = select(DepartmentModel)
        if search:
            query = query.where(DepartmentModel.name.contains(search))
        result = await db.execute(query)
        departments = result.scalars().all()
        rows = _build_tree_from_departments(departments)
        total = len(departments)
    else:
        departments, total = await crud_department.get_multi_with_filter(
            db, skip=skip, limit=limit, tree=False, search=search
        )
        rows = [_serialize_department(dept) for dept in departments]

    return {"data": rows, "total": total, "skip": skip, "limit": limit}


@router.get("/tree", response_model=List[dict])
async def get_departments_tree(db: AsyncSession = Depends(get_async_db)):
    """
    获取部门树结构。
    """
    result = await db.execute(select(DepartmentModel))
    departments = result.scalars().all()
    return _build_tree_from_departments(departments)


@router.get("/options", response_model=List[dict])
async def get_department_options(db: AsyncSession = Depends(get_async_db)):
    """
    获取部门下拉选项。
    """
    departments, _ = await crud_department.get_multi_with_filter(db, tree=False)
    return [
        {"id": dept.id, "label": dept.name, "value": dept.id, "parentId": dept.parent_id}
        for dept in departments
    ]


@router.get("/stats", response_model=dict)
async def get_department_stats(db: AsyncSession = Depends(get_async_db)):
    """
    获取部门统计信息。
    """
    departments, total = await crud_department.get_multi_with_filter(db, tree=False)

    dept_user_counts: Dict[int, int] = {}
    for dept in departments:
        count_stmt = select(func.count(AdminUser.id)).where(AdminUser.department_id == dept.id)
        count_result = await db.execute(count_stmt)
        dept_user_counts[dept.id] = int(count_result.scalar() or 0)

    return {
        "total_departments": total,
        "active_departments": sum(1 for dept in departments if bool(dept.status)),
        "inactive_departments": sum(1 for dept in departments if not bool(dept.status)),
        "department_user_counts": dept_user_counts,
        "total_users_in_departments": sum(dept_user_counts.values()),
    }


@router.get("/{id}", response_model=dict)
async def get_department(*, id: int, db: AsyncSession = Depends(get_async_db)):
    """
    获取单个部门。
    """
    department = await crud_department.get(db, id=id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return _serialize_department(department)


@router.post("/", response_model=dict)
async def create_department(*, department_in: DepartmentCreate, db: AsyncSession = Depends(get_async_db)):
    """
    创建部门。
    """
    existing = await crud_department.get_by_name(db, name=department_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Department name already exists")
    department = await crud_department.create(db, obj_in=department_in)
    return _serialize_department(department)


@router.put("/{id}", response_model=dict)
async def update_department(
    *, id: int, department_in: DepartmentUpdate, db: AsyncSession = Depends(get_async_db)
):
    """
    更新部门。
    """
    department = await crud_department.get(db, id=id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    if department_in.name and department_in.name != department.name:
        existing = await crud_department.get_by_name(db, name=department_in.name)
        if existing and existing.id != id:
            raise HTTPException(status_code=400, detail="Department name already exists")

    updated = await crud_department.update(db, db_obj=department, obj_in=department_in)
    return _serialize_department(updated)


@router.patch("/{id}/status", response_model=dict)
async def update_department_status(
    *, id: int, payload: DepartmentStatusUpdateRequest, db: AsyncSession = Depends(get_async_db)
):
    """
    更新部门状态。
    """
    department = await crud_department.get(db, id=id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    status_bool = _normalize_status(payload.status)
    updated = await crud_department.update(db, db_obj=department, obj_in={"status": status_bool})
    return {"message": "Department status updated", "data": _serialize_department(updated)}


@router.patch("/{id}/move", response_model=dict)
async def move_department(*, id: int, payload: DepartmentMoveRequest, db: AsyncSession = Depends(get_async_db)):
    """
    移动部门到新的父级。
    """
    department = await crud_department.get(db, id=id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    if payload.parent_id == id:
        raise HTTPException(status_code=400, detail="Cannot set department parent to itself")

    if payload.parent_id is not None:
        parent = await crud_department.get(db, id=payload.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent department not found")

    updated = await crud_department.update(db, db_obj=department, obj_in={"parent_id": payload.parent_id})
    return {"message": "Department moved", "data": _serialize_department(updated)}


@router.delete("/batch", response_model=dict)
async def batch_delete_departments(
    *, payload: DepartmentBatchDeleteRequest, db: AsyncSession = Depends(get_async_db)
):
    """
    批量删除部门。
    """
    if not payload.ids:
        raise HTTPException(status_code=400, detail="Department id list cannot be empty")

    deleted: List[int] = []
    skipped: List[Dict[str, Any]] = []

    for dept_id in payload.ids:
        department = await crud_department.get(db, id=dept_id)
        if not department:
            skipped.append({"id": dept_id, "reason": "not_found"})
            continue

        children = await crud_department.get_children(db, parent_id=dept_id)
        if children:
            skipped.append({"id": dept_id, "reason": "has_children"})
            continue

        user_count_stmt = select(func.count(AdminUser.id)).where(AdminUser.department_id == dept_id)
        user_count_result = await db.execute(user_count_stmt)
        if int(user_count_result.scalar() or 0) > 0:
            skipped.append({"id": dept_id, "reason": "has_members"})
            continue

        await crud_department.remove(db, id=dept_id)
        deleted.append(dept_id)

    return {"message": "Batch delete finished", "deleted": deleted, "skipped": skipped}


@router.delete("/{id}", response_model=dict)
async def delete_department(*, id: int, db: AsyncSession = Depends(get_async_db)):
    """
    删除部门。
    """
    department = await crud_department.get(db, id=id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    children = await crud_department.get_children(db, parent_id=id)
    if children:
        raise HTTPException(status_code=400, detail="Cannot delete department with children")

    user_count_stmt = select(func.count(AdminUser.id)).where(AdminUser.department_id == id)
    user_count_result = await db.execute(user_count_stmt)
    if int(user_count_result.scalar() or 0) > 0:
        raise HTTPException(status_code=400, detail="Cannot delete department with users assigned")

    await crud_department.remove(db, id=id)
    return {"message": "Department deleted successfully"}


@router.get("/{id}/members", response_model=dict)
async def get_department_members(
    *, id: int, db: AsyncSession = Depends(get_async_db), skip: int = 0, limit: int = 100
):
    """
    获取部门成员。
    """
    department = await crud_department.get(db, id=id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    stmt = select(AdminUser).where(AdminUser.department_id == id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    users = result.scalars().all()

    count_stmt = select(func.count(AdminUser.id)).where(AdminUser.department_id == id)
    count_result = await db.execute(count_stmt)
    total = int(count_result.scalar() or 0)

    user_list = [AdminUserResponse.model_validate(user).model_dump() for user in users]
    return {"data": user_list, "total": total, "skip": skip, "limit": limit}


@router.post("/{department_id}/members/{user_id}", response_model=dict)
async def assign_user_to_department(
    department_id: int, user_id: int, db: AsyncSession = Depends(get_async_db)
):
    """
    将单个用户分配到部门。
    """
    department = await crud_department.get(db, id=department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    user_stmt = select(AdminUser).where(AdminUser.id == user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.department_id = department_id
    await db.commit()
    await db.refresh(user)
    return {"message": "User assigned to department successfully", "user_id": user_id, "department_id": department_id}


@router.post("/{department_id}/members", response_model=dict)
async def batch_assign_users_to_department(
    department_id: int, payload: DepartmentMembersRequest, db: AsyncSession = Depends(get_async_db)
):
    """
    批量将用户分配到部门。
    """
    department = await crud_department.get(db, id=department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    user_ids = payload.normalized_user_ids()
    if not user_ids:
        raise HTTPException(status_code=400, detail="User id list cannot be empty")

    updated: List[int] = []
    not_found: List[int] = []
    for user_id in user_ids:
        user_stmt = select(AdminUser).where(AdminUser.id == user_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        if not user:
            not_found.append(user_id)
            continue
        user.department_id = department_id
        updated.append(user_id)

    await db.commit()
    return {"message": "Batch assign finished", "department_id": department_id, "updated": updated, "not_found": not_found}


@router.delete("/{department_id}/members/batch", response_model=dict)
async def batch_remove_users_from_department(
    department_id: int, payload: DepartmentMembersRequest, db: AsyncSession = Depends(get_async_db)
):
    """
    批量将用户从部门移除。
    """
    department = await crud_department.get(db, id=department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    user_ids = payload.normalized_user_ids()
    if not user_ids:
        raise HTTPException(status_code=400, detail="User id list cannot be empty")

    removed: List[int] = []
    not_found: List[int] = []
    for user_id in user_ids:
        user_stmt = select(AdminUser).where(AdminUser.id == user_id).where(AdminUser.department_id == department_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        if not user:
            not_found.append(user_id)
            continue
        user.department_id = None
        removed.append(user_id)

    await db.commit()
    return {"message": "Batch remove finished", "department_id": department_id, "removed": removed, "not_found": not_found}


@router.delete("/{department_id}/members/{user_id}", response_model=dict)
async def remove_user_from_department(
    department_id: int, user_id: int, db: AsyncSession = Depends(get_async_db)
):
    """
    将单个用户从部门移除。
    """
    department = await crud_department.get(db, id=department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    user_stmt = select(AdminUser).where(AdminUser.id == user_id).where(AdminUser.department_id == department_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found in this department")

    user.department_id = None
    await db.commit()
    return {"message": "User removed from department successfully", "user_id": user_id, "department_id": department_id}
