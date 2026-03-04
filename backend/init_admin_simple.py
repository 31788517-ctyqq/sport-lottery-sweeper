#!/usr/bin/env python3
"""
简单管理员初始化脚本
"""

import sys
import os
from datetime import datetime
from contextlib import contextmanager

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.core.security import get_password_hash
from backend.models.admin_user import AdminUser, AdminRoleEnum, AdminStatusEnum
from backend.core.database import SessionLocal

def init_admin_user():
    """初始化管理员用户"""
    db = SessionLocal()
    
    try:
        # 检查是否已存在管理员用户
        existing_admin = db.query(AdminUser).filter(AdminUser.username == 'admin').first()
        
        if existing_admin:
            print(f"管理员用户已存在: {existing_admin.username}")
            print(f"ID: {existing_admin.id}")
            print(f"邮箱: {existing_admin.email}")
            return
        
        # 创建超级管理员
        admin_user = AdminUser(
            username='admin',
            email='admin@example.com',
            password_hash=get_password_hash('admin123'),
            real_name='系统管理员',
            role=AdminRoleEnum.SUPER_ADMIN,
            status=AdminStatusEnum.ACTIVE,
            is_verified=True,
            login_count=0,
            department='系统管理部',
            position='系统管理员'
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ 管理员用户创建成功!")
        print(f"用户名: {admin_user.username}")
        print(f"密码: admin123")
        print(f"邮箱: {admin_user.email}")
        print(f"角色: {admin_user.role.value}")
        print(f"状态: {admin_user.status.value}")
        
    except Exception as e:
        print(f"❌ 创建管理员用户失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    init_admin_user()