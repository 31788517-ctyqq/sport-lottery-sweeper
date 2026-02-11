#!/usr/bin/env python3
"""
认证API路由模块
处理用户注册、登录、认证等相关API端点
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta
import jwt
import bcrypt
from sqlalchemy.orm import Session

# AI_WORKING: coder1 @2026-01-26 - 修复相对导入
from backend.core.database import SessionLocal
# AI_DONE: coder1 @2026-01-26
# AI_WORKING: coder1 @2026-01-26 - 修复相对导入
from backend.models.admin_user import AdminUser, AdminRoleEnum, AdminStatusEnum
# AI_DONE: coder1 @2026-01-26
# AI_WORKING: coder1 @2026-01-26 - 修复相对导入
from backend.core.security import verify_password
from backend.config import settings
from backend.services.user_activity_logger import get_user_activity_logger
from backend.api.deps import get_current_user
from backend.database import get_db
# AI_DONE: coder1 @2026-01-26

router = APIRouter()

# API标签常量
TAG_AUTH = "🔐 认证"
TAG_USERS = "👤 用户"

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

class UserLogin(BaseModel):
    """用户登录请求模型"""
    username: str = Field(..., description="用户名", min_length=3, max_length=50)
    password: str = Field(..., description="密码", min_length=6)

class TokenResponse(BaseModel):
    """令牌响应模型"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="访问令牌过期时间（秒）")
    user_info: dict = Field(..., description="用户信息")

class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str = Field(..., description="刷新令牌")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    创建JWT访问令牌
    
    Args:
        data: 要编码到令牌中的数据
        expires_delta: 令牌过期时间，如果为None则使用默认值
        
    Returns:
        编码后的JWT令牌字符串
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """
    创建JWT刷新令牌
    
    Args:
        data: 要编码到令牌中的数据
        
    Returns:
        编码后的JWT刷新令牌字符串
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="用户登录",
    description="""
    用户使用用户名和密码进行登录认证。
    
    ### 认证流程
    1. 验证用户名和密码
    2. 检查用户状态是否为ACTIVE
    3. 生成访问令牌和刷新令牌
    4. 更新用户最后登录时间和登录次数
    
    ### 安全说明
    - 密码使用bcrypt进行安全哈希存储
    - 访问令牌有效期：{access_expire}分钟
    - 刷新令牌有效期：7天
    - 失败的登录尝试会被记录用于安全审计
    """.format(access_expire=ACCESS_TOKEN_EXPIRE_MINUTES),
    responses={
        200: {
            "description": "登录成功",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 1800
                    }
                }
            }
        },
        401: {
            "description": "认证失败",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_credentials": {
                            "summary": "用户名或密码错误",
                            "value": {"detail": "用户名或密码错误"}
                        },
                        "inactive_user": {
                            "summary": "用户账户被禁用",
                            "value": {"detail": "用户账户已被禁用或未激活"}
                        }
                    }
                }
            }
        }
    }
)
async def login(login_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """
    用户登录接口
    """
    # 获取客户端信息
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # AI_WORKING: coder1 @2026-02-10 - 添加调试日志
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Login attempt: username={login_data.username}, password_length={len(login_data.password)}")
    # AI_DONE: coder1 @2026-02-10
    
    # 从数据库查询用户
    user = db.query(AdminUser).filter(AdminUser.username == login_data.username).first()
    
    if not user:
        # 记录失败的登录尝试
        activity_logger = get_user_activity_logger(db)
        activity_logger.log_user_login(
            user_id=0,  # 未知用户
            username=login_data.username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason="用户不存在"
        )
        # AI_WORKING: coder1 @2026-02-10 - 添加调试日志
        logger.warning(f"User not found: {login_data.username}")
        # AI_DONE: coder1 @2026-02-10
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 验证密码
    if not verify_password(login_data.password, user.password_hash):
        # 记录失败的登录尝试
        activity_logger = get_user_activity_logger(db)
        activity_logger.log_user_login(
            user_id=user.id,
            username=user.username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason="密码错误"
        )
        # AI_WORKING: coder1 @2026-02-10 - 添加调试日志
        logger.warning(f"Password verification failed for user: {user.username}")
        logger.warning(f"Stored hash: {user.password_hash}")
        logger.warning(f"Input password length: {len(login_data.password)}")
        # AI_DONE: coder1 @2026-02-10
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # AI_WORKING: coder1 @2026-01-28 - 修复用户状态验证逻辑
    # 检查用户状态 - 使用正确的枚举值比较
    if not user.status or user.status != AdminStatusEnum.ACTIVE:
        # 记录失败的登录尝试
        activity_logger = get_user_activity_logger(db)
        activity_logger.log_user_login(
            user_id=user.id,
            username=user.username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason="用户账户被禁用"
        )
        raise HTTPException(status_code=401, detail="用户账户已被禁用或未激活")
    # AI_DONE: coder1 @2026-01-28
    
    # 生成访问令牌和刷新令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        {
            "sub": user.username,
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
        },
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token({
        "sub": user.username,
        "user_id": user.id,
    })
    
    # 更新最后登录时间和登录次数
    user.last_login_at = datetime.utcnow()
    user.login_count += 1
    db.commit()
    
    # AI_WORKING: coder1 @2026-02-10 - 添加调试日志
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Login successful for user: {user.username}")
    logger.info(f"User attributes: department={getattr(user, 'department', 'MISSING')}, position={getattr(user, 'position', 'MISSING')}")
    # AI_DONE: coder1 @2026-02-10
    
    # 记录成功的登录事件
    activity_logger = get_user_activity_logger(db)
    activity_logger.log_user_login(
        user_id=user.id,
        username=user.username,
        ip_address=ip_address,
        user_agent=user_agent,
        success=True
    )
    
    # AI_WORKING: coder1 @2026-01-28 - 修复返回数据的字段处理，确保安全访问
    # 生成用户信息，对所有可能为空的字段进行安全处理
    user_info = {
        "userId": user.id,
        "username": user.username,
        "email": user.email,
        "real_name": user.real_name or '',
        "roles": [user.role.value] if user.role else ['operator'],
        "status": user.status.value if user.status else 'inactive',
        "department": getattr(user, 'department', '') or '',
        "position": getattr(user, 'position', '') or '',
        "phone": getattr(user, 'phone', '') or '',
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "login_count": user.login_count or 0
    }
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_info=user_info
    )
# AI_DONE: coder1 @2026-01-28

@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="刷新访问令牌",
    description="""
    使用刷新令牌获取新的访问令牌。
    
    ### 使用场景
    - 访问令牌过期后无需重新登录
    - 保持用户会话连续性
    - 提高用户体验
    
    ### 安全说明
    - 刷新令牌只能使用一次（可选实现）
    - 刷新令牌有独立的过期时间（7天）
    - 无效的刷新令牌会被拒绝
    """,
    responses={
        200: {
            "description": "令牌刷新成功",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 1800
                    }
                }
            }
        },
        401: {
            "description": "刷新令牌无效或已过期",
            "content": {
                "application/json": {
                    "example": {"detail": "无效的刷新令牌"}
                }
            }
        }
    }
)
async def refresh_token(refresh_request: RefreshTokenRequest, request: Request, db: Session = Depends(get_db)):
    """
    刷新访问令牌接口
    """
    try:
        # 获取客户端信息
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # 验证刷新令牌
        payload = jwt.decode(refresh_request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(status_code=401, detail="无效的令牌类型")
            
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="无效的刷新令牌")
            
        # 验证用户是否存在且状态正常
        user = db.query(AdminUser).filter(AdminUser.id == user_id).first()
        if not user or user.username != username:
            raise HTTPException(status_code=401, detail="用户不存在")
            
        if not user.status or user.status != AdminStatusEnum.ACTIVE:
            raise HTTPException(status_code=401, detail="用户账户已被禁用")
            
        # 生成新的访问令牌和刷新令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            {
                "sub": user.username,
                "user_id": user.id,
                "username": user.username,
                "role": user.role.value,
            },
            expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token({
            "sub": user.username,
            "user_id": user.id,
        })
        
        # 记录令牌刷新事件
        activity_logger = get_user_activity_logger(db)
        activity_logger.log_token_refresh(
            user_id=user.id,
            username=user.username,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return {
            "code": 200,
            "message": "令牌刷新成功",
            "data": {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="刷新令牌已过期")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="无效的刷新令牌")

@router.post(
    "/logout",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="用户登出",
    description="""
    用户登出系统。
    
    ### 功能说明
    - 记录用户登出事件到活动日志
    - 返回登出成功消息
    
    ### 注意事项
    - 前端需要清除本地存储的令牌
    - JWT令牌本身无法在服务端失效，但会记录登出事件用于审计
    """,
    responses={
        200: {
            "description": "登出成功",
            "content": {
                "application/json": {
                    "example": {
                        "message": "登出成功"
                    }
                }
            }
        }
    }
)
async def logout(request: Request, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    用户登出接口
    """
    # 获取客户端信息
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # 记录登出事件
    activity_logger = get_user_activity_logger(db)
    activity_logger.log_user_logout(
        user_id=current_user["user_id"],
        username=current_user["username"],
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return {"message": "登出成功"}
