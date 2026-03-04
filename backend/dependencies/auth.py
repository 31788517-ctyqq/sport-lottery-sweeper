#!/usr/bin/env python3
"""
认证依赖注入模块
提供FastAPI路由的依赖项函数
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Optional

from database_utils import get_db
from ..models.user import User, UserStatus, UserRole, UserType, SocialProvider
from models.admin_user import AdminUser, AdminStatusEnum
from core.security import SECRET_KEY, ALGORITHM
from core.exceptions import AuthenticationError, AuthorizationError

# HTTP Bearer认证方案
security = HTTPBearer(auto_error=False)

def get_token_from_header(request: Request) -> Optional[str]:
    """从请求头中获取JWT令牌"""
    authorization = request.headers.get("Authorization")
    
    if not authorization:
        return None
    
    scheme, token = get_authorization_scheme_param(authorization)
    if scheme.lower() != "bearer":
        return None
    
    return token

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """获取当前认证的用户"""
    token = get_token_from_header(request)
    
    if not token:
        raise AuthenticationError("Not authenticated")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise AuthenticationError("Invalid token")
            
    except JWTError:
        raise AuthenticationError("Invalid token")
    
    # 查询用户
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise AuthenticationError("User not found")
    
    # 检查用户状态
    if user.status != UserStatusEnum.ACTIVE:
        raise AuthenticationError("User account is disabled")
    
    return user

def get_current_admin_user(
    request: Request,
    db: Session = Depends(get_db)
) -> AdminUser:
    """获取当前认证的管理员用户"""
    token = get_token_from_header(request)
    
    if not token:
        raise AuthenticationError("Not authenticated")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id = payload.get("sub")
        token_type = payload.get("type")
        user_role = payload.get("role")
        
        if admin_id is None or token_type != "access":
            raise AuthenticationError("Invalid token")
            
    except JWTError:
        raise AuthenticationError("Invalid token")
    
    # 查询管理员用户
    admin = db.query(AdminUser).filter(AdminUser.id == int(admin_id)).first()
    if not admin:
        raise AuthenticationError("Admin not found")
    
    # 检查管理员状态
    if admin.status != AdminStatusEnum.ACTIVE:
        raise AuthenticationError("Admin account is disabled")
    
    # 检查角色权限（确保有管理员权限）
    if admin.role not in ["admin", "super_admin"]:
        raise AuthorizationError("Admin privileges required")
    
    return admin

def get_current_super_admin_user(
    current_admin: AdminUser = Depends(get_current_admin_user)
) -> AdminUser:
    """获取当前认证的超级管理员用户"""
    if current_admin.role != "super_admin":
        raise AuthorizationError("Super admin privileges required")
    
    return current_admin

def get_optional_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """获取可选的当前用户（用于公开接口）"""
    try:
        return get_current_user(request, db)
    except AuthenticationError:
        return None

def require_permission(permission: str):
    """权限检查装饰器依赖项"""
    def permission_checker(
        current_admin: AdminUser = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
    ) -> AdminUser:
        # TODO: 实现细粒度权限检查逻辑
        # 这里可以根据admin.permissions字段检查具体权限
        
        # 临时实现：super_admin拥有所有权限
        if current_admin.role == "super_admin":
            return current_admin
        
        # 检查具体权限
        if hasattr(current_admin, 'permissions') and current_admin.permissions:
            permissions_list = current_admin.permissions if isinstance(current_admin.permissions, list) else []
            if permission in permissions_list:
                return current_admin
        
        raise AuthorizationError(f"Permission '{permission}' required")
    
    return permission_checker

def get_client_info(request: Request) -> dict:
    """获取客户端信息"""
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "referer": request.headers.get("referer"),
    }

# 辅助函数
def get_authorization_scheme_param(authorization_header: str):
    """解析Authorization头"""
    if not authorization_header:
        return None, None
    
    scheme, _, param = authorization_header.partition(" ")
    return scheme, param