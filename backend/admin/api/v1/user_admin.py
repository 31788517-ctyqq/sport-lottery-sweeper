"""
用户管理API端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...deps import get_current_admin
from .... import crud
from ....schemas.user import UserResponse
from ....schemas.response import UnifiedResponse, PageResponse
from ....api.deps import get_db

router = APIRouter(prefix="/users", tags=["admin-users"])


@router.get("/", response_model=UnifiedResponse[PageResponse[UserResponse]])
async def list_users(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页大小"),
    status: Optional[str] = Query(None, description="用户状态过滤"),
    role: Optional[str] = Query(None, description="角色过滤"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """
    获取用户列表
    """
    try:
        skip = (page - 1) * size
        users = await crud.user.get_multi(db, skip=skip, limit=size)
        
        # 转换为响应模型
        user_responses = []
        for user in users:
            user_responses.append(UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.first_name + " " + user.last_name if user.first_name and user.last_name else user.nickname or user.username,
                is_active=user.is_verified,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at
            ))
        
        # 获取总数（带过滤条件）
        count_query = select(func.count(User.id))
        if status:
            count_query = count_query.where(User.status == status)
        if role:
            count_query = count_query.where(User.role == role)
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        
        return UnifiedResponse.success(PageResponse(
            data=user_responses,
            total=total,
            page=page,
            size=size
        ))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=UnifiedResponse[UserResponse])
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """
    获取用户详情
    """
    try:
        user = await crud.user.get(db, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        user_response = UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.first_name + " " + user.last_name if user.first_name and user.last_name else user.nickname or user.username,
            is_active=user.is_verified,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
        return UnifiedResponse.success(user_response)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/status", response_model=UnifiedResponse[dict])
async def update_user_status(
    user_id: int,
    status: str = Query(..., description="新状态"),
    db: AsyncSession = Depends(get_db)
):
    """
    更新用户状态
    """
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        user.status = status
        user.updated_at = datetime.utcnow()
        await db.commit()
        
        return UnifiedResponse.success({"message": "用户状态更新成功"})
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}", response_model=UnifiedResponse[dict])
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """
    删除用户
    """
    try:
        user = await crud.user.get(db, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        await crud.user.remove(db, id=user_id)
        
        return UnifiedResponse.success({"message": "用户删除成功"})
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# 已在文件头部导入所需组件