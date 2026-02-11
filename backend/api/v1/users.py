#!/usr/bin/env python3
"""
用户管理API路由
提供用户的增删改查等RESTful接口
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from datetime import datetime
import os
import uuid
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic.networks import EmailStr

from backend.database import get_db
from backend.models.user import User, UserStatus
from backend.models.admin_user import AdminUser, AdminRoleEnum, AdminStatusEnum
from backend.schemas.user import (
    UserCreate, UserUpdate, UserResponse, 
    AdminUserCreate, AdminUserUpdate, AdminUserResponse,
    UserListResponse, AdminUserListResponse
)
from backend.core.security import get_password_hash
from backend.api.deps import get_current_user, get_current_admin_user
from backend.services.user_activity_logger import get_user_activity_logger

router = APIRouter(prefix="/users", tags=["用户管理"])

# 配置头像存储路径
AVATAR_UPLOAD_DIR = Path("uploads/avatars")
AVATAR_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_AVATAR_TYPES = {"image/jpeg", "image/png", "image/gif"}

class UserProfileUpdate(BaseModel):
    """个人资料更新请求模型"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    gender: Optional[str] = Field(None, description="性别")
    birthday: Optional[str] = Field(None, description="生日 (YYYY-MM-DD)")

def save_avatar_file(file: UploadFile) -> str:
    """
    保存头像文件到服务器
    
    Args:
        file: 上传的文件对象
        
    Returns:
        保存后的文件相对路径
        
    Raises:
        HTTPException: 文件验证失败
    """
    # 验证文件类型
    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件类型。支持的类型: {', '.join(ALLOWED_AVATAR_TYPES)}"
        )
    
    # 验证文件大小
    file.file.seek(0, 2)  # 移动到文件末尾
    file_size = file.file.tell()
    file.file.seek(0)  # 重置到文件开头
    
    if file_size > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"文件大小超过限制 ({MAX_AVATAR_SIZE // 1024 // 1024}MB)"
        )
    
    # 生成唯一文件名
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = AVATAR_UPLOAD_DIR / unique_filename
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    
    return f"/uploads/avatars/{unique_filename}"

# ==================== 普通用户管理 ====================

@router.post(
    "/register", 
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="""
    新用户注册接口。
    
    ### 注册要求
    - 用户名长度3-50字符
    - 密码长度至少8位
    - 邮箱格式必须有效
    - 手机号可选但必须唯一
    
    ### 安全说明
    - 密码使用bcrypt哈希存储
    - 用户默认状态为ACTIVE
    - 用户类型默认为free（免费用户）
    """,
    responses={
        201: {"description": "用户注册成功"},
        409: {
            "description": "用户名、邮箱或手机号已存在",
            "content": {
                "application/json": {
                    "examples": {
                        "username_exists": {"value": {"detail": "用户名已存在"}},
                        "email_exists": {"value": {"detail": "邮箱已被注册"}},
                        "phone_exists": {"value": {"detail": "手机号已被注册"}}
                    }
                }
            }
        }
    }
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
    "/profile",
    response_model=UserResponse,
    summary="获取当前用户个人资料",
    description="获取当前认证用户的完整个人资料信息",
    responses={
        200: {"description": "获取个人资料成功"},
        401: {"description": "未认证或令牌无效"},
        404: {"description": "用户不存在"}
    }
)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的个人资料"""
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UserResponse.from_orm(user)

@router.put(
    "/profile",
    response_model=UserResponse,
    summary="更新个人资料",
    description="""
    更新当前用户的个人资料信息。
    
    ### 可更新字段
    - 昵称 (nickname)
    - 邮箱 (email) - 需要重新验证
    - 手机号 (phone) - 需要重新验证
    - 个人简介 (bio)
    - 性别 (gender)
    - 生日 (birthday)
    - 头像 (avatar) - URL格式
    
    ### 注意事项
    - 用户名不可修改
    - 修改邮箱或手机号后需要重新验证
    - 密码修改需要单独的密码修改接口
    """,
    responses={
        200: {"description": "个人资料更新成功"},
        400: {"description": "请求数据验证失败"},
        401: {"description": "未认证"},
        404: {"description": "用户不存在"},
        409: {"description": "邮箱或手机号已存在"}
    }
)
async def update_profile(
    request: Request,
    user_update: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户的个人资料"""
    # 获取客户端信息
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # 获取当前用户
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新用户信息
    update_data = user_update.dict(exclude_unset=True)
    
    # 检查邮箱是否已存在（排除当前用户）
    if "email" in update_data and update_data["email"]:
        existing_email = db.query(User).filter(
            User.email == update_data["email"],
            User.id != user.id
        ).first()
        if existing_email:
            raise HTTPException(status_code=409, detail="邮箱已被其他用户使用")
    
    # 检查手机号是否已存在（排除当前用户）
    if "phone" in update_data and update_data["phone"]:
        existing_phone = db.query(User).filter(
            User.phone == update_data["phone"],
            User.id != user.id
        ).first()
        if existing_phone:
            raise HTTPException(status_code=409, detail="手机号已被其他用户使用")
    
    # 更新字段
    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    # 记录用户资料更新事件
    activity_logger = get_user_activity_logger(db)
    activity_logger.log_profile_update(
        user_id=user.id,
        username=user.username,
        updated_fields=update_data,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return UserResponse.from_orm(user)

@router.post(
    "/profile/avatar",
    response_model=dict,
    summary="上传用户头像",
    description="""
    上传用户头像图片。
    
    ### 上传要求
    - 支持格式: JPEG, PNG, GIF
    - 文件大小限制: 5MB
    - 自动重命名避免冲突
    
    ### 返回值
    - avatar_url: 上传后的头像URL
    - message: 操作结果消息
    """,
    responses={
        200: {
            "description": "头像上传成功",
            "content": {
                "application/json": {
                    "example": {
                        "avatar_url": "/uploads/avatars/123e4567-e89b-12d3-a456-426614174000.jpg",
                        "message": "头像上传成功"
                    }
                }
            }
        },
        400: {"description": "文件格式或大小不符合要求"},
        401: {"description": "未认证"},
        404: {"description": "用户不存在"}
    }
)
async def upload_avatar(
    request: Request,
    avatar: UploadFile = File(..., description="头像图片文件"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传用户头像"""
    # 获取客户端信息
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # 获取当前用户
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 保存头像文件
    avatar_url = save_avatar_file(avatar)
    
    # 更新用户头像URL
    user.avatar = avatar_url
    user.updated_at = datetime.utcnow()
    db.commit()
    
    # 记录头像上传事件
    activity_logger = get_user_activity_logger(db)
    activity_logger.log_avatar_upload(
        user_id=user.id,
        username=user.username,
        avatar_url=avatar_url,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return {
        "avatar_url": avatar_url,
        "message": "头像上传成功"
    }

@router.put(
    "/profile/password",
    response_model=dict,
    summary="修改用户密码",
    description="""
    修改当前用户的密码。
    
    ### 安全要求
    - 需要提供当前密码进行验证
    - 新密码长度至少8位
    - 新密码和确认密码必须匹配
    
    ### 返回值
    - message: 操作结果消息
    """,
    responses={
        200: {"description": "密码修改成功"},
        400: {"description": "密码验证失败或新密码不符合要求"},
        401: {"description": "未认证或当前密码错误"}
    }
)
async def change_password(
    request: Request,
    current_password: str = Form(..., description="当前密码"),
    new_password: str = Form(..., min_length=8, description="新密码"),
    confirm_password: str = Form(..., description="确认新密码"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改用户密码"""
    from backend.core.security import verify_password
    
    # 验证新密码和确认密码
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="新密码和确认密码不匹配")
    
    # 获取当前用户
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 验证当前密码
    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="当前密码错误")
    
    # 更新密码
    user.hashed_password = get_password_hash(new_password)
    user.updated_at = datetime.utcnow()
    db.commit()
    
    # 记录密码修改事件
    activity_logger = get_user_activity_logger(db)
    activity_logger.log_password_change(
        user_id=user.id,
        username=user.username,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return {"message": "密码修改成功"}