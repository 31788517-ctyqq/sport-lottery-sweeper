"""
管理员认证模块
专门处理 admin_users 表的认证逻辑
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from ..models.admin_user import AdminUser
from ..core.security import verify_password
from ..schemas.auth import LoginRequest

def authenticate_admin_user(db: Session, username: str, password: str):
    """
    管理员用户认证函数
    查询 admin_users 表进行认证
    
    Args:
        db: 数据库会话
        username: 用户名
        password: 明文密码
        
    Returns:
        AdminUser: 认证成功的用户对象，失败返回None
    """
    # 查询管理员用户
    admin_user = db.query(AdminUser).filter(
        AdminUser.username == username,
        AdminUser.status == "active"
    ).first()
    
    if not admin_user:
        return None
    
    # 验证密码
    if verify_password(password, admin_user.password_hash):
        # 更新登录信息
        admin_user.last_login_at = func.now()
        admin_user.login_count += 1
        db.commit()
        db.refresh(admin_user)
        return admin_user
    
    # 密码错误，增加失败次数
    admin_user.failed_login_attempts += 1
    db.commit()
    return None
