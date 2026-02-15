#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临时登录API - 用于解决策略保存的认证问题
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt

from backend.core.database import get_db
from backend.models.admin_user import AdminUser
from backend.config import settings

# 创建路由器
router = APIRouter(prefix="/api/v1", tags=["login"])

# 临时硬编码密码验证（仅用于开发测试）
# admin用户的密码是 admin123
TEMP_PASSWORD_HASH = "$2b$12$etVELtOpdoNTLKhtPppf4.V6SOZd8By31N20ow78h85KBUkr96A7a"

@router.post("/token")
async def login(username: str, password: str, db: Session = Depends(get_db)):
    """临时登录API - 生成JWT token"""
    try:
        # 查找用户
        user = db.query(AdminUser).filter(AdminUser.username == username).first()
        if not user:
            raise HTTPException(status_code=400, detail="用户名或密码错误")
        
        # 临时密码验证（仅比较哈希值）
        if user.password_hash != TEMP_PASSWORD_HASH:
            raise HTTPException(status_code=400, detail="用户名或密码错误")
        
        # 检查用户状态
        if user.status != "active":
            raise HTTPException(status_code=400, detail="用户账户已被禁用")
        
        # 生成JWT token
        expire = datetime.utcnow() + timedelta(hours=24)
        token_data = {
            "sub": user.username,
            "user_id": user.id,
            "role": user.role,
            "exp": expire
        }
        
        token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 86400,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")

@router.get("/users/me")
async def get_current_user_info(username: str, db: Session = Depends(get_db)):
    """临时获取当前用户信息API"""
    try:
        user = db.query(AdminUser).filter(AdminUser.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "status": user.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")
