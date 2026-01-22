"""
后台管理用户管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

# 简化的导入，避免复杂依赖
from backend import crud, models, schemas
from backend.database_async import get_async_db
from backend.core.security import get_current_active_admin_user
from backend.utils.response import UnifiedResponse

router = APIRouter()


@router.get("/", response_model=UnifiedResponse[schemas.AdminUserListResponse])
async def list_admin_users(
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页最大记录数"),
    role: Optional[schemas.AdminRoleEnum] = Query(None, description="按角色筛选"),
    status: Optional[schemas.AdminStatusEnum] = Query(None, description="按状态筛选"),
    department: Optional[str] = Query(None, description="按部门筛选"),
    search: Optional[str] = Query(None, description="按用户名/真实姓名/邮箱搜索")
):
    """
    获取后台用户列表（分页）
    """
    users, total = await crud.admin_user.get_multi(
        db, skip=skip, limit=limit, role=role, status=status,
        department=department, search=search
    )
    
    return UnifiedResponse.success(data=schemas.AdminUserListResponse(
        items=users,
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    ))


@router.post("/", response_model=UnifiedResponse[schemas.AdminUserResponse])
async def create_admin_user(
    user_in: schemas.AdminUserCreate,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    创建后台用户
    """
    # 检查用户名和邮箱是否已存在
    existing_user = await crud.admin_user.get_by_username(db, user_in.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    existing_email = await crud.admin_user.get_by_email(db, user_in.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已被使用")
    
    user = await crud.admin_user.create(db, obj_in=user_in, created_by=current_admin.id)
    return UnifiedResponse.success(data=user)


@router.get("/{user_id}", response_model=UnifiedResponse[schemas.AdminUserDetailResponse])
async def get_admin_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    获取后台用户详情
    """
    user = await crud.admin_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 添加创建者姓名信息
    if user.created_by:
        creator = await crud.admin_user.get(db, id=user.created_by)
        user.creator_name = creator.real_name if creator else None
    else:
        user.creator_name = "系统"
    
    return UnifiedResponse.success(data=user)


@router.put("/{user_id}", response_model=UnifiedResponse[schemas.AdminUserResponse])
async def update_admin_user(
    user_id: int,
    user_update: schemas.AdminUserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    更新后台用户信息
    """
    user = await crud.admin_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    updated_user = await crud.admin_user.update(db, db_obj=user, obj_in=user_update)
    return UnifiedResponse.success(data=updated_user)


@router.put("/{user_id}/status", response_model=UnifiedResponse[schemas.AdminUserResponse])
async def update_admin_user_status(
    user_id: int,
    status: schemas.AdminStatusEnum = Query(..., description="新状态"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    更新后台用户状态
    """
    user = await crud.admin_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    updated_user = await crud.admin_user.update_status(db, db_obj=user, status=status)
    return UnifiedResponse.success(data=updated_user)


@router.put("/{user_id}/reset-password", response_model=UnifiedResponse[dict])
async def reset_admin_user_password(
    user_id: int,
    password_reset: schemas.AdminUserResetPassword,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    重置后台用户密码
    """
    user = await crud.admin_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    await crud.admin_user.reset_password(db, db_obj=user, obj_in=password_reset)
    return UnifiedResponse.success(data={"message": "密码重置成功"})


@router.delete("/{user_id}", response_model=UnifiedResponse[dict])
async def delete_admin_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    删除后台用户（软删除）
    """
    success = await crud.admin_user.remove(db, id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UnifiedResponse.success(data={"message": "用户删除成功"})


@router.get("/stats", response_model=UnifiedResponse[schemas.AdminUserStatsResponse])
async def get_admin_user_stats(
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    获取后台用户统计信息
    """
    stats = await crud.admin_user.get_stats(db)
    return UnifiedResponse.success(data=schemas.AdminUserStatsResponse(**stats))