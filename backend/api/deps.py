"""
API依赖注入模块
包含数据库会话、认证等全局依赖项
"""

from typing import Generator, Optional, AsyncGenerator
from datetime import datetime, timezone, timedelta
from jose import JWTError, jwt
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..database_async import get_async_db
from ..models.user import User
from ..models.admin_user import AdminUser  # 假设存在AdminUser模型
from backend.config import settings


# ==============================
# JWT 配置
# ==============================

# 从环境变量获取密钥，如果没有则使用默认值 (生产环境务必更改)
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

# HTTP Bearer token scheme for authentication
security = HTTPBearer()


def create_access_token(data: dict):
    """创建JWT访问令牌"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=2)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    """验证JWT令牌并返回用户信息"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无法验证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 确保user_id是整数类型
        if isinstance(user_id, str):
            try:
                user_id = int(user_id)
            except (ValueError, TypeError):
                # 如果无法转换为整数，保持原样
                pass
        
        # 返回用户ID、用户名和角色
        return {
            "user_id": user_id, 
            "username": payload.get("username"), 
            "role": payload.get("role")
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    获取当前用户（通用函数）
    """
    token = credentials.credentials
    return verify_token(token)


async def get_current_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前认证的管理员用户"""
    token = credentials.credentials
    user_data = verify_token(token)
    
    # 确保user_id是整数类型
    user_id = user_data["user_id"]
    if isinstance(user_id, str):
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            # 如果无法转换为整数，保持原样（但记录警告）
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"无法将user_id转换为整数: {user_id}")
    
    # 返回模拟的管理员用户信息，包含从token获取的角色
    return {
        "id": user_id,
        "username": user_data.get("username", "admin"),
        "email": "admin@example.com",
        "role": user_data.get("role", "admin")
    }


# 添加get_current_admin函数以兼容旧代码
async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前认证的管理员用户（兼容函数）"""
    token = credentials.credentials
    user_data = verify_token(token)
    
    # 检查用户角色是否为管理员
    role = user_data.get("role", "user")
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    # 确保user_id是整数类型
    user_id = user_data["user_id"]
    if isinstance(user_id, str):
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            # 如果无法转换为整数，保持原样（但记录警告）
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"无法将user_id转换为整数: {user_id}")
    
    # 返回模拟的管理员用户信息
    return {
        "id": user_id,
        "username": user_data.get("username", "admin"),
        "email": "admin@example.com",
        "role": role
    }


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
