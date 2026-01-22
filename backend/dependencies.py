"""
依赖注入模块
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from .core.database import SessionLocal, get_db
from .core.auth import verify_password, get_password_hash
from .models.user import User
from .config import settings

# OAuth2密码承载流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    获取当前认证用户
    
    Args:
        db: 数据库会话
        token: JWT令牌
        
    Returns:
        User: 当前用户
        
    Raises:
        HTTPException: 认证失败
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证失败",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    
    return user

def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前管理员用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 管理员用户
        
    Raises:
        HTTPException: 权限不足
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    return current_user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 活跃用户
    """
    return current_user

def verify_websocket_token(token: str) -> Optional[str]:
    """
    验证WebSocket令牌
    
    Args:
        token: JWT令牌
        
    Returns:
        Optional[str]: 用户ID或None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        return username
    except JWTError:
        return None

# 密码验证相关依赖
def validate_password_strength(password: str) -> bool:
    """
    验证密码强度
    
    Args:
        password: 密码
        
    Returns:
        bool: 密码是否足够强壮
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False
    
    if len(password) > settings.PASSWORD_MAX_LENGTH:
        return False
    
    # 检查是否包含数字
    if not any(char.isdigit() for char in password):
        return False
    
    # 检查是否包含字母
    if not any(char.isalpha() for char in password):
        return False
    
    # 检查是否包含特殊字符
    special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?"
    if not any(char in special_chars for char in password):
        return False
    
    return True

def get_password_hasher():
    """
    获取密码哈希器
    
    Returns:
        function: 密码哈希函数
    """
    return get_password_hash

def get_password_verifier():
    """
    获取密码验证器
    
    Returns:
        function: 密码验证函数
    """
    return verify_password