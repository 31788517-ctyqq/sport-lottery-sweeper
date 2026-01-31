#!/usr/bin/env python3
"""
用户管理API路由
提供用户的增删改查等RESTful接口
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.database_utils import get_db
from backend.models.user import User, UserStatus
from backend.models.admin_user import AdminUser, AdminRoleEnum, AdminStatusEnum
from backend.schemas.user import (
    UserCreate, UserUpdate, UserResponse, 
    AdminUserCreate, AdminUserUpdate, AdminUserResponse,
    UserListResponse, AdminUserListResponse
)
from backend.core.security import get_password_hash
from backend.api.deps import get_current_user, get_current_admin_user

router = APIRouter(prefix="/users", tags=["用户管理"])

# ==================== 普通用户管理 ====================

@router.post(
    "/register", 
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="新用户注册接口"
)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="用户名已存在")
    
    # 检查邮箱是否已存在
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=409, detail="邮箱已被注册")
    
    # 检查手机号是否已存在
    if user_data.phone:
        existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
        if existing_phone:
            raise HTTPException(status_code=409, detail="手机号已被注册")
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        nickname=user_data.nickname,
        phone=user_data.phone,
        avatar=user_data.avatar,
        status=UserStatus.ACTIVE,
        user_type="free"  # 默认免费用户
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse.from_orm(db_user)

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="获取用户信息",
    description="根据用户ID获取用户详细信息"
)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户信息"""
    # 检查权限：只能查看自己的信息或者管理员
    if current_user["user_id"] != user_id and not (hasattr(current_user, 'role') and current_user.get('role') == 'admin'):
        raise HTTPException(status_code=403, detail="无权限查看其他用户信息")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UserResponse.from_orm(user)

@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="更新用户信息",
    description="更新用户基本信息"
)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户信息"""
    # 检查权限：只能更新自己的信息或管理员可以更新他人信息
    is_admin = current_user.get('role') == 'admin'
    if current_user["user_id"] != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="无权限修改其他用户信息")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新用户信息
    update_data = user_update.dict(exclude_unset=True)
    
    # 如果更新密码，需要重新哈希
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return UserResponse.from_orm(user)

# ==================== 个人资料更新端点 ====================

@router.put(
    "/profile",
    response_model=UserResponse,
    summary="更新个人资料",
    description="更新当前用户的个人资料信息"
)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户的个人资料"""
    # 获取当前用户
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新用户信息（只更新允许的字段）
    update_data = user_update.dict(exclude_unset=True)
    
    # 如果更新密码，需要重新哈希
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]
    
    for field, value in update_data.items():
        if field in ["username", "email", "nickname", "phone", "avatar", "bio", "description", "gender", "birthday"]:
            setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return UserResponse.from_orm(user)

@router.get(
    "/profile",
    response_model=UserResponse,
    summary="获取个人资料",
    description="获取当前用户的个人资料信息"
)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的个人资料"""
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UserResponse.from_orm(user)

# ==================== 其他用户管理功能 ====================

@router.get(
    "/",
    response_model=UserListResponse,
    summary="获取用户列表",
    description="分页获取用户列表（管理员功能）"
)
async def list_users(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[UserStatus] = Query(None, description="用户状态"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取用户列表（仅管理员）"""
    # 检查权限：只有管理员可以查看用户列表
    is_admin = current_user.get('role') in ['admin', 'super_admin']
    if not is_admin:
        raise HTTPException(status_code=403, detail="无权限查看用户列表")
    
    query = db.query(User)
    
    # 搜索过滤
    if search:
        query = query.filter(
            User.username.contains(search) |
            User.email.contains(search) |
            User.nickname.contains(search)
        )
    
    # 状态过滤
    if status:
        query = query.filter(User.status == status)
    
    # 计算总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * size
    users = query.offset(offset).limit(size).all()
    
    return UserListResponse(
        users=[UserResponse.from_orm(user) for user in users],
        total=total,
        page=page,
        size=size
    )

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除用户",
    description="删除用户（软删除，仅管理员）"
)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """删除用户（仅管理员）"""
    # 检查权限：只有管理员可以删除用户
    is_admin = current_user.get('role') in ['admin', 'super_admin']
    if not is_admin:
        raise HTTPException(status_code=403, detail="无权限删除用户")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 软删除：修改状态为禁用
    user.status = UserStatus.INACTIVE
    user.updated_at = datetime.utcnow()
    db.commit()

# ==================== 用户状态管理 ====================

@router.put(
    "/{user_id}/status",
    response_model=dict,
    summary="更新用户状态",
    description="更新用户状态（仅管理员）"
)
async def update_user_status(
    user_id: int,
    status: UserStatus = Query(..., description="新状态"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """更新用户状态（仅管理员）"""
    # 检查权限：只有管理员可以更新用户状态
    is_admin = current_user.get('role') in ['admin', 'super_admin']
    if not is_admin:
        raise HTTPException(status_code=403, detail="无权限更新用户状态")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新用户状态
    user.status = status
    user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "用户状态更新成功", "user_id": user_id, "new_status": status.value}

@router.post(
    "/{user_id}/password/reset",
    response_model=dict,
    summary="重置用户密码",
    description="重置用户密码（仅管理员）"
)
async def reset_user_password(
    user_id: int,
    new_password: str = Query(..., min_length=6, description="新密码"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """重置用户密码（仅管理员）"""
    # 检查权限：只有管理员可以重置用户密码
    is_admin = current_user.get('role') in ['admin', 'super_admin']
    if not is_admin:
        raise HTTPException(status_code=403, detail="无权限重置用户密码")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新用户密码
    user.hashed_password = get_password_hash(new_password)
    user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "用户密码重置成功", "user_id": user_id}

# ==================== 管理员用户管理 ====================

@router.post(
    "/admin",
    response_model=AdminUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建管理员",
    description="创建新的管理员用户（仅超级管理员）"
)
async def create_admin_user(
    admin_data: AdminUserCreate,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """创建管理员用户（仅超级管理员）"""
    # 检查权限：只有超级管理员可以创建管理员
    if current_user.role != AdminRoleEnum.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="只有超级管理员可以创建管理员")
    
    # 检查用户名是否已存在
    existing_admin = db.query(AdminUser).filter(AdminUser.username == admin_data.username).first()
    if existing_admin:
        raise HTTPException(status_code=409, detail="管理员用户名已存在")
    
    # 检查邮箱是否已存在
    existing_email = db.query(AdminUser).filter(AdminUser.email == admin_data.email).first()
    if existing_email:
        raise HTTPException(status_code=409, detail="管理员邮箱已被注册")
    
    # 创建管理员用户
    hashed_password = get_password_hash(admin_data.password)
    
    db_admin = AdminUser(
        username=admin_data.username,
        email=admin_data.email,
        hashed_password=hashed_password,
        full_name=admin_data.full_name,
        role=admin_data.role,
        status=AdminStatusEnum.ACTIVE,
        phone=admin_data.phone,
        department=admin_data.department,
        permissions=admin_data.permissions
    )
    
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    
    return AdminUserResponse.from_orm(db_admin)

@router.get(
    "/admin/{admin_id}",
    response_model=AdminUserResponse,
    summary="获取管理员信息",
    description="根据ID获取管理员详细信息"
)
async def get_admin_user(
    admin_id: int,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取管理员信息"""
    # 检查权限：只能查看自己的信息或者超级管理员
    if current_user.id != admin_id and current_user.role != AdminRoleEnum.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="无权限查看其他管理员信息")
    
    admin = db.query(AdminUser).filter(AdminUser.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="管理员不存在")
    
    return AdminUserResponse.from_orm(admin)

@router.get(
    "/admin",
    response_model=AdminUserListResponse,
    summary="获取管理员列表",
    description="分页获取管理员列表（仅超级管理员）"
)
async def list_admin_users(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    role: Optional[AdminRoleEnum] = Query(None, description="管理员角色"),
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取管理员列表（仅超级管理员）"""
    # 检查权限：只有超级管理员可以查看管理员列表
    if current_user.role != AdminRoleEnum.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="只有超级管理员可以查看管理员列表")
    
    query = db.query(AdminUser)
    
    # 搜索过滤
    if search:
        query = query.filter(
            AdminUser.username.contains(search) |
            AdminUser.email.contains(search) |
            AdminUser.full_name.contains(search)
        )
    
    # 角色过滤
    if role:
        query = query.filter(AdminUser.role == role)
    
    # 计算总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * size
    admins = query.offset(offset).limit(size).all()
    
    return AdminUserListResponse(
        admins=[AdminUserResponse.from_orm(admin) for admin in admins],
        total=total,
        page=page,
        size=size
    )