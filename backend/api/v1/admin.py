"""
Admin API routes
Merged version: contains login interface and sub-route registration functionality
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

# Import models and schemas
from ...schemas.auth import LoginRequest, LoginResponse
from ...core.auth import create_access_token
from ...core.admin_auth import authenticate_admin_user
from ...models.admin_user import AdminUser
from ...config import settings
from ...database import get_db

logger = logging.getLogger("api.v1.admin")

router = APIRouter(tags=["admin"])

# ===== Login interface (from file A) =====
@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    管理员登录接口
    
    Args:
        login_data: 登录凭证
        db: 数据库会话
        
    Returns:
        LoginResponse: 登录结果
    """
    # 使用管理员专用认证函数
    admin_user = authenticate_admin_user(db, login_data.username, login_data.password)
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin_user.username, "type": "admin"},
        expires_delta=access_token_expires
    )
    
    # 构建 full_name
    full_name = admin_user.real_name or ""
    
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": admin_user.id,
                "username": admin_user.username,
                "email": admin_user.email,
                "full_name": full_name,
                "is_superuser": admin_user.role == "admin",
                "role": admin_user.role,
                "created_at": admin_user.created_at.isoformat() if admin_user.created_at else None
            }
        }
    }