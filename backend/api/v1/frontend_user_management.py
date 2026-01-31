"""
前台用户管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

# 使用绝对导入修复路径问题
import sys
import os
# 设置路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 直接导入所需模块
from backend import crud, models
from backend.schemas.user import UserTypeEnum, UserStatusEnum, UserCreate, UserUpdate, UserResponse, UserListResponse
from backend.database_async import get_async_db
from backend.core.security import get_current_active_admin_user
from backend.utils.response import UnifiedResponse

router = APIRouter()


@router.get("/", response_model=UnifiedResponse[UserListResponse])
async def list_users(
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页最大记录数"),
    user_type: Optional[UserTypeEnum] = Query(None, description="按用户类型筛选"),
    status: Optional[UserStatusEnum] = Query(None, description="按状态筛选"),
    search: Optional[str] = Query(None, description="按用户名/昵称/邮箱搜索")
):
    """
    获取前台用户列表（分页）
    """
    users, total = await crud.user.get_multi(
        db, skip=skip, limit=limit, user_type=user_type, status=status, search=search
    )
    
    return UnifiedResponse.success(data=UserListResponse(
        items=users,
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    ))


@router.post("/", response_model=UnifiedResponse[UserResponse])
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    创建前台用户
    """
    # 检查用户名和邮箱是否已存在
    existing_user = await crud.user.get_by_username(db, user_in.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    existing_email = await crud.user.get_by_email(db, user_in.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已被使用")
    
    user = await crud.user.create(db, obj_in=user_in)
    return UnifiedResponse.success(data=user)


@router.get("/{user_id}", response_model=UnifiedResponse[UserResponse])
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    获取前台用户详情
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UnifiedResponse.success(data=user)


@router.put("/{user_id}", response_model=UnifiedResponse[UserResponse])
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    更新前台用户信息
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    updated_user = await crud.user.update(db, db_obj=user, obj_in=user_update)
    return UnifiedResponse.success(data=updated_user)


@router.put("/{user_id}/status", response_model=UnifiedResponse[UserResponse])
async def update_user_status(
    user_id: int,
    status: UserStatusEnum = Query(..., description="新状态"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    更新前台用户状态
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 直接更新状态字段
    user.status = status
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return UnifiedResponse.success(data=user)


@router.put("/{user_id}/reset-password", response_model=UnifiedResponse[dict])
async def reset_user_password(
    user_id: int,
    new_password: str = Query(..., min_length=8, description="新密码"),
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    重置前台用户密码
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新密码
    from backend.core.auth import get_password_hash
    user.password_hash = get_password_hash(new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return UnifiedResponse.success(data={"message": "密码重置成功"})


@router.delete("/{user_id}", response_model=UnifiedResponse[dict])
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_admin: models.AdminUser = Depends(get_current_active_admin_user)
):
    """
    删除前台用户
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 从数据库中删除用户
    await db.delete(user)
    await db.commit()
    
    return UnifiedResponse.success(data={"message": "用户删除成功"})