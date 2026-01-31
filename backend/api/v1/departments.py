from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
# 使用正确的依赖导入
from backend.database_async import get_async_db
from backend.schemas.department import (
    Department,
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentWithChildren
)
from backend.crud.department import crud_department

router = APIRouter()


@router.get("/", response_model=dict)
async def get_departments(
    db: AsyncSession = Depends(get_async_db),
    skip: int = 0,
    limit: int = 100,
    tree: bool = False,
    search: Optional[str] = None
):
    """
    获取部门列表，支持树形结构
    """
    departments, total = await crud_department.get_multi_with_filter(
        db, skip=skip, limit=limit, tree=tree, search=search
    )
    return {
        "data": departments,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/tree", response_model=List[DepartmentWithChildren])
async def get_departments_tree(db: AsyncSession = Depends(get_async_db)):
    """
    获取部门树形结构
    """
    departments, _ = await crud_department.get_multi_with_filter(db, tree=True)
    return departments


@router.get("/{id}", response_model=Department)
async def get_department(
    *,
    id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取单个部门信息
    """
    department = await crud_department.get(db, id=id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@router.post("/", response_model=Department)
async def create_department(
    *,
    department_in: DepartmentCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    创建部门
    """
    # 检查部门名称是否已存在
    existing_dept = await crud_department.get_by_name(db, name=department_in.name)
    if existing_dept:
        raise HTTPException(status_code=400, detail="Department name already exists")
    
    department = await crud_department.create(db, obj_in=department_in)
    return department


@router.put("/{id}", response_model=Department)
async def update_department(
    *,
    id: int,
    department_in: DepartmentUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    更新部门信息
    """
    department = await crud_department.get(db, id=id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # 检查部门名称是否与其他同名部门冲突
    if department_in.name and department_in.name != department.name:
        existing_dept = await crud_department.get_by_name(db, name=department_in.name)
        if existing_dept and existing_dept.id != id:
            raise HTTPException(status_code=400, detail="Department name already exists")
    
    department = await crud_department.update(db, db_obj=department, obj_in=department_in)
    return department


@router.delete("/{id}")
async def delete_department(
    *,
    id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """
    删除部门
    """
    department = await crud_department.get(db, id=id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # 检查是否有子部门
    children = await crud_department.get_children(db, parent_id=id)
    if children:
        raise HTTPException(status_code=400, detail="Cannot delete department with children")
    
    await crud_department.remove(db, id=id)
    return {"msg": "Department deleted successfully"}


@router.get("/options", response_model=List[dict])
async def get_department_options(
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取部门选项（扁平结构），用于下拉选择
    """
    departments, _ = await crud_department.get_multi_with_filter(db, tree=False)
    options = [{"id": dept.id, "label": dept.name, "value": dept.id} for dept in departments]
    return options


@router.get("/{id}/members", response_model=dict)
async def get_department_members(
    *,
    id: int,
    db: AsyncSession = Depends(get_async_db),
    skip: int = 0,
    limit: int = 100
):
    """
    获取部门成员
    """
    from backend.models.admin_user import AdminUser
    from backend.schemas.admin_user import AdminUserResponse
    
    department = await crud_department.get(db, id=id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # 获取属于该部门的用户
    stmt = select(AdminUser).where(AdminUser.department_id == id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    users = result.scalars().all()
    
    # 获取总数量
    count_stmt = select(func.count(AdminUser.id)).where(AdminUser.department_id == id)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()
    
    # 使用Pydantic模型转换
    user_list = [AdminUserResponse.model_validate(user) for user in users]
    
    return {
        "data": user_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/stats", response_model=dict)
async def get_department_stats(
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取部门统计信息
    """
    departments, total = await crud_department.get_multi_with_filter(db, tree=False)
    
    stats = {
        "total_departments": total,
        "active_departments": sum(1 for d in departments if d.status),
        "inactive_departments": sum(1 for d in departments if not d.status)
    }
    
    return stats