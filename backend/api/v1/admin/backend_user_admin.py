"""
后台用户管理API
用于管理具有后台权限的运营人员和管理员
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from backend.database import get_async_session
from backend.models.admin_user import AdminUser, AdminRoleEnum, AdminStatusEnum
from backend.schemas.admin_user import (
    AdminUserCreate, AdminUserUpdate, AdminUserResponse, AdminUserListResponse,
    AdminUserDetailResponse, AdminUserChangePassword, AdminUserResetPassword,
    AdminUserStatsResponse, AdminOperationLogListResponse, AdminLoginLogListResponse
)
from backend.crud.admin_user import admin_user, admin_operation_log, admin_login_log

router = APIRouter()


@router.get("/backend-users", response_model=AdminUserListResponse)
async def get_backend_users(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（用户名/真实姓名/邮箱）"),
    role: Optional[AdminRoleEnum] = Query(None, description="角色"),
    status: Optional[AdminStatusEnum] = Query(None, description="状态"),
    department: Optional[str] = Query(None, description="部门"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    获取后台用户列表
    支持分页、搜索和筛选
    """
    skip = (page - 1) * size
    
    try:
        items, total = await admin_user.get_multi(
            db=db,
            skip=skip,
            limit=size,
            role=role,
            status=status,
            department=department,
            search=search
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
            detail=f"获取后台用户列表失败: {str(e)}"
        )


@router.get("/backend-users/{user_id}", response_model=AdminUserDetailResponse)
async def get_backend_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """获取后台用户详情"""
    user_obj = await admin_user.get(db, user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="后台用户不存在"
        )
    
    # 获取创建者名称
    creator_name = None
    if user_obj.created_by:
        creator = await admin_user.get(db, user_obj.created_by)
        if creator:
            creator_name = creator.real_name
    
    response_data = AdminUserDetailResponse.model_validate(user_obj)
    response_data.creator_name = creator_name
    
    return response_data


@router.post("/backend-users", response_model=AdminUserResponse)
async def create_backend_user(
    user_in: AdminUserCreate,
    request: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """
    创建后台用户
    需要超级管理员或管理员权限
    """
    # 检查用户名是否已存在
    existing_user = await admin_user.get_by_username(db, user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    existing_email = await admin_user.get_by_email(db, user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    try:
        # TODO: 从token中获取当前管理员ID
        current_admin_id = None
        
        new_user = await admin_user.create(db, user_in, created_by=current_admin_id)
        
        # 记录操作日志
        await admin_operation_log.create(
            db=db,
            admin_id=current_admin_id or 0,
            action="create",
            resource_type="admin_user",
            resource_id=str(new_user.id),
            resource_name=new_user.username,
            method="POST",
            path="/api/v1/admin/backend-users",
            status_code=201,
            ip_address=request.client.host if request.client else ""
        )
        
        return new_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建后台用户失败: {str(e)}"
        )


@router.put("/backend-users/{user_id}", response_model=AdminUserResponse)
async def update_backend_user(
    user_id: int,
    user_in: AdminUserUpdate,
    request: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """更新后台用户信息"""
    user_obj = await admin_user.get(db, user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="后台用户不存在"
        )
    
    # 如果更新邮箱，检查是否已存在
    if user_in.email and user_in.email != user_obj.email:
        existing_email = await admin_user.get_by_email(db, user_in.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
    
    try:
        updated_user = await admin_user.update(db, user_obj, user_in)
        
        # 记录操作日志
        # TODO: 从token中获取当前管理员ID
        current_admin_id = 0
        await admin_operation_log.create(
            db=db,
            admin_id=current_admin_id,
            action="update",
            resource_type="admin_user",
            resource_id=str(user_id),
            resource_name=updated_user.username,
            method="PUT",
            path=f"/api/v1/admin/backend-users/{user_id}",
            status_code=200,
            ip_address=request.client.host if request.client else ""
        )
        
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新后台用户失败: {str(e)}"
        )


@router.patch("/backend-users/{user_id}/status")
async def update_backend_user_status(
    user_id: int,
    new_status: AdminStatusEnum,
    request: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """更新后台用户状态"""
    user_obj = await admin_user.get(db, user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="后台用户不存在"
        )
    
    try:
        updated_user = await admin_user.update_status(db, user_obj, new_status)
        
        # 记录操作日志
        current_admin_id = 0
        await admin_operation_log.create(
            db=db,
            admin_id=current_admin_id,
            action="update_status",
            resource_type="admin_user",
            resource_id=str(user_id),
            resource_name=updated_user.username,
            method="PATCH",
            path=f"/api/v1/admin/backend-users/{user_id}/status",
            status_code=200,
            ip_address=request.client.host if request.client else "",
            changes_after={"status": new_status.value}
        )
        
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


@router.post("/backend-users/{user_id}/change-password")
async def change_backend_user_password(
    user_id: int,
    password_in: AdminUserChangePassword,
    request: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """修改后台用户密码（用户自己操作）"""
    user_obj = await admin_user.get(db, user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="后台用户不存在"
        )
    
    success = await admin_user.change_password(db, user_obj, password_in)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 记录操作日志
    await admin_operation_log.create(
        db=db,
        admin_id=user_id,
        action="change_password",
        resource_type="admin_user",
        resource_id=str(user_id),
        resource_name=user_obj.username,
        method="POST",
        path=f"/api/v1/admin/backend-users/{user_id}/change-password",
        status_code=200,
        ip_address=request.client.host if request.client else ""
    )
    
    return {
        "code": 200,
        "message": "密码修改成功",
        "data": None
    }


@router.post("/backend-users/{user_id}/reset-password")
async def reset_backend_user_password(
    user_id: int,
    password_in: AdminUserResetPassword,
    request: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """重置后台用户密码（管理员操作）"""
    user_obj = await admin_user.get(db, user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="后台用户不存在"
        )
    
    try:
        await admin_user.reset_password(db, user_obj, password_in)
        
        # 记录操作日志
        current_admin_id = 0  # TODO: 从token获取
        await admin_operation_log.create(
            db=db,
            admin_id=current_admin_id,
            action="reset_password",
            resource_type="admin_user",
            resource_id=str(user_id),
            resource_name=user_obj.username,
            method="POST",
            path=f"/api/v1/admin/backend-users/{user_id}/reset-password",
            status_code=200,
            ip_address=request.client.host if request.client else ""
        )
        
        return {
            "code": 200,
            "message": "密码重置成功",
            "data": None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重置密码失败: {str(e)}"
        )


@router.delete("/backend-users/{user_id}")
async def delete_backend_user(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """删除后台用户（软删除）"""
    user_obj = await admin_user.get(db, user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="后台用户不存在"
        )
    
    # 不能删除超级管理员
    if user_obj.role == AdminRoleEnum.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="不能删除超级管理员"
        )
    
    try:
        await admin_user.remove(db, user_id)
        
        # 记录操作日志
        current_admin_id = 0  # TODO: 从token获取
        await admin_operation_log.create(
            db=db,
            admin_id=current_admin_id,
            action="delete",
            resource_type="admin_user",
            resource_id=str(user_id),
            resource_name=user_obj.username,
            method="DELETE",
            path=f"/api/v1/admin/backend-users/{user_id}",
            status_code=200,
            ip_address=request.client.host if request.client else ""
        )
        
        return {
            "code": 200,
            "message": "后台用户删除成功",
            "data": {"user_id": user_id}
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除后台用户失败: {str(e)}"
        )


@router.get("/backend-users/stats/overview", response_model=AdminUserStatsResponse)
async def get_backend_user_stats(
    db: AsyncSession = Depends(get_async_session)
):
    """获取后台用户统计信息"""
    try:
        stats = await admin_user.get_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )


@router.get("/backend-users/{user_id}/operation-logs", response_model=AdminOperationLogListResponse)
async def get_user_operation_logs(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_session)
):
    """获取后台用户操作日志"""
    user_obj = await admin_user.get(db, user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="后台用户不存在"
        )
    
    skip = (page - 1) * size
    
    try:
        items, total = await admin_operation_log.get_multi(
            db=db,
            skip=skip,
            limit=size,
            admin_id=user_id,
            action=action,
            resource_type=resource_type
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
            detail=f"获取操作日志失败: {str(e)}"
        )


@router.get("/backend-users/{user_id}/login-logs", response_model=AdminLoginLogListResponse)
async def get_user_login_logs(
    user_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    success: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_async_session)
):
    """获取后台用户登录日志"""
    user_obj = await admin_user.get(db, user_id)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="后台用户不存在"
        )
    
    skip = (page - 1) * size
    
    try:
        items, total = await admin_login_log.get_multi(
            db=db,
            skip=skip,
            limit=size,
            admin_id=user_id,
            success=success
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
            detail=f"获取登录日志失败: {str(e)}"
        )
