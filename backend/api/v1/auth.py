#!/usr/bin/env python3
"""
认证API路由模块
处理用户注册、登录、认证等相关API端点
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
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
# AI_DONE: coder1 @2026-01-26

router = APIRouter()

# API标签常量
TAG_AUTH = "🔐 认证"
TAG_USERS = "👤 用户"

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 7200

class UserLogin(BaseModel):
    username: str
    password: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口
    """
    # 从数据库查询用户
    user = db.query(AdminUser).filter(AdminUser.username == login_data.username).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # 验证密码
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    # AI_WORKING: coder1 @2026-01-28 - 修复用户状态验证逻辑
    # 检查用户状态 - 使用正确的枚举值比较
    if not user.status or user.status != AdminStatusEnum.ACTIVE:
        raise HTTPException(status_code=401, detail="用户账户已被禁用或未激活")
    # AI_DONE: coder1 @2026-01-28
    
    # 生成访问令牌
    access_token = create_access_token({
        "user_id": user.id,
        "username": user.username,
        "role": user.role.value,
    })
    
    # 更新最后登录时间和登录次数
    user.last_login_at = datetime.utcnow()
    user.login_count += 1
    db.commit()
    
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
    
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "user_info": user_info
        }
    }
# AI_DONE: coder1 @2026-01-28
