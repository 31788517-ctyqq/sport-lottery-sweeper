"""
前台用户管理API
用于管理使用前台系统的普通用户
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime

from backend.database_utils import get_async_session
from backend.models.user import User, UserStatus, UserType, UserRole, SocialProvider
from backend.schemas.user import UserResponse, UserList, UserUpdate
from backend.crud.user import user as crud_user

router = APIRouter()


@router.get("/users", response_model=UserList)
async def get_frontend_users(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（用户名/邮箱/昵称）"),
    status: Optional[UserStatusEnum] = Query(None, description="用户状态"),
    user_type: Optional[UserTypeEnum] = Query(None, description="用户类型"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    获取前台用户列表
    支持分页、搜索和筛选
    """
    skip = (page - 1) * size
    
    try:
        items, total = await crud_user.get_multi(
            db=db,
            skip=skip,
            limit=size,
            search=search,
            status=status,
            user_type=user_type,
            start_date=start_date,
            end_date=end_date
        )
        
        pages = (total + size - 1) // size
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户列表失败: {str(e)}"
        )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_frontend_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """获取前台用户详情"""
    user_obj = await crud_user.get(db, user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user_obj


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_frontend_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    """更新前台用户信息"""
    user_obj = await crud_user.get(db, user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    try:
        updated_user = await crud_user.update(db, user_obj, user_in)
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户失败: {str(e)}"
        )


@router.patch("/users/{user_id}/status")
async def update_frontend_user_status(
    user_id: int,
    new_status: UserStatusEnum,
    db: AsyncSession = Depends(get_async_session)
):
    """更新前台用户状态"""
    user_obj = await crud_user.get(db, user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    try:
        updated_user = await crud_user.update_status(db, user_obj, new_status)
        return {
            "code": 200,
            "message": "状态更新成功",
            "data": {
                "user_id": user_id,
                "status": new_status.value
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新状态失败: {str(e)}"
        )


@router.patch("/users/{user_id}/type")
async def update_frontend_user_type(
    user_id: int,
    new_type: UserTypeEnum,
    db: AsyncSession = Depends(get_async_session)
):
    """更新前台用户类型（普通用户/高级用户/分析师）"""
    user_obj = await crud_user.get(db, user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    try:
        user_obj.user_type = new_type
        user_obj.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user_obj)
        
        return {
            "code": 200,
            "message": "用户类型更新成功",
            "data": {
                "user_id": user_id,
                "user_type": new_type.value
            }
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户类型失败: {str(e)}"
        )


@router.delete("/users/{user_id}")
async def delete_frontend_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """删除前台用户（软删除）"""
    user_obj = await crud_user.get(db, user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    try:
        # 软删除：将状态设置为banned
        user_obj.status = UserStatusEnum.BANNED
        user_obj.updated_at = datetime.utcnow()
        await db.commit()
        
        return {
            "code": 200,
            "message": "用户删除成功",
            "data": {"user_id": user_id}
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除用户失败: {str(e)}"
        )


@router.get("/users/stats/overview")
async def get_frontend_user_stats(
    db: AsyncSession = Depends(get_async_session)
):
    """获取前台用户统计信息"""
    try:
        stats = await crud_user.get_stats(db)
        return {
            "code": 200,
            "message": "获取统计信息成功",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )


@router.get("/users/{user_id}/activities")
async def get_user_activities(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session)
):
    """获取用户活动日志"""
    user_obj = await crud_user.get(db, user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # TODO: 实现活动日志查询
    return {
        "code": 200,
        "message": "获取活动日志成功",
        "data": {
            "items": [],
            "total": 0,
            "page": page,
            "size": size,
            "pages": 0
        }
    }


@router.get("/users/{user_id}/login-logs")
async def get_user_login_logs(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session)
):
    """获取用户登录日志"""
    user_obj = await crud_user.get(db, user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # TODO: 实现登录日志查询
    return {
        "code": 200,
        "message": "获取登录日志成功",
        "data": {
            "items": [],
            "total": 0,
            "page": page,
            "size": size,
            "pages": 0
        }
    }


@router.post("/users/batch-delete")
async def batch_delete_users(
    user_ids: List[int],
    db: AsyncSession = Depends(get_async_session)
):
    """批量删除用户"""
    try:
        deleted_count = 0
        for user_id in user_ids:
            user_obj = await crud_user.get(db, user_id)
            if user_obj:
                user_obj.status = UserStatusEnum.BANNED
                user_obj.updated_at = datetime.utcnow()
                deleted_count += 1
        
        await db.commit()
        
        return {
            "code": 200,
            "message": f"成功删除 {deleted_count} 个用户",
            "data": {
                "deleted_count": deleted_count,
                "total_requested": len(user_ids)
            }
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量删除失败: {str(e)}"
        )


@router.post("/users/batch-update-status")
async def batch_update_user_status(
    user_ids: List[int],
    new_status: UserStatusEnum,
    db: AsyncSession = Depends(get_async_session)
):
    """批量更新用户状态"""
    try:
        updated_count = 0
        for user_id in user_ids:
            user_obj = await crud_user.get(db, user_id)
            if user_obj:
                user_obj.status = new_status
                user_obj.updated_at = datetime.utcnow()
                updated_count += 1
        
        await db.commit()
        
        return {
            "code": 200,
            "message": f"成功更新 {updated_count} 个用户状态",
            "data": {
                "updated_count": updated_count,
                "total_requested": len(user_ids),
                "new_status": new_status.value
            }
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量更新状态失败: {str(e)}"
        )
