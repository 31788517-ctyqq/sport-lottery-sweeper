"""
认证API端点
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any

# 使用正确的相对导入
from ...config import settings
from ...schemas.auth import Token, UserCreate, UserResponse
from ...core.auth_service import AuthService
from ...api.deps import get_current_user

# 创建实例
auth_service = AuthService()

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录接口
    """
    user = await auth_service.authenticate_user(
        form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(user.username)
    refresh_token = auth_service.create_refresh_token(user.username)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """
    用户注册接口
    """
    user = await auth_service.create_user(user_data)
    return user


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """
    获取当前用户信息
    """
    return current_user
