#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化管理员角色和用户
一次性插入角色、权限、用户，解决后台登录问题
"""
import sys
import os
import bcrypt
from datetime import datetime

# 获取项目根目录路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 现在可以导入backend模块
from backend.core.database import SessionLocal
from backend.models.user import User, UserRole, UserStatus, UserType
from backend.models.role import Role
from backend.models.permission import Permission
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from backend.config import settings

# 密码哈希函数
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def init_admin_data():
    # 使用与后端相同的数据库引擎
    db_engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=db_engine)
    db = Session()
    
    try:
        # 1. 插入角色
        print("插入系统角色...")
        roles_data = [
            {"name": "超级管理员", "code": "super_admin", "description": "系统超级管理员，拥有所有权限", "is_active": True},
            {"name": "管理员", "code": "admin", "description": "系统管理员，拥有大部分管理权限", "is_active": True},
            {"name": "分析师", "code": "analyst", "description": "数据分析师，可以查看和分析所有数据", "is_active": True},
            {"name": "高级用户", "code": "premium", "description": "高级用户，可以查看所有情报和高级功能", "is_active": True},
            {"name": "普通用户", "code": "normal", "description": "普通用户，只能查看基本情报", "is_active": True},
        ]
        
        role_map = {}  # code -> role_id
        for role_data in roles_data:
            # 检查角色是否已存在
            existing = db.query(Role).filter(Role.code == role_data["code"]).first()
            if not existing:
                role = Role(**role_data)
                db.add(role)
                db.flush()  # 获取ID但不提交
                role_map[role_data["code"]] = role.id
                print(f"  创建角色: {role_data['name']} ({role_data['code']})")
            else:
                role_map[role_data["code"]] = existing.id
                print(f"  角色已存在: {role_data['name']} ({role_data['code']})")
        
        db.commit()
        
        # 2. 插入权限
        print("\n插入系统权限...")
        permissions_data = [
            # 管理员权限
            {"name": "访问管理后台", "code": "admin.access", "resource": "admin", "action": "access", "is_active": True},
            {"name": "查看爬虫配置", "code": "crawler.read", "resource": "crawler", "action": "read", "is_active": True},
            {"name": "管理爬虫配置", "code": "crawler.manage", "resource": "crawler", "action": "manage", "is_active": True},
            # 用户管理权限
            {"name": "查看用户列表", "code": "user.read", "resource": "user", "action": "read", "is_active": True},
            {"name": "创建用户", "code": "user.create", "resource": "user", "action": "create", "is_active": True},
            {"name": "编辑用户", "code": "user.update", "resource": "user", "action": "update", "is_active": True},
            {"name": "删除用户", "code": "user.delete", "resource": "user", "action": "delete", "is_active": True},
        ]
        
        for perm_data in permissions_data:
            existing = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
            if not existing:
                perm = Permission(**perm_data)
                db.add(perm)
                print(f"  创建权限: {perm_data['name']} ({perm_data['code']})")
        
        db.commit()
        
        # 3. 给管理员角色分配权限
        print("\n给管理员角色分配权限...")
        admin_role = db.query(Role).filter(Role.code == "admin").first()
        super_admin_role = db.query(Role).filter(Role.code == "super_admin").first()
        
        # 获取所有权限
        all_permissions = db.query(Permission).all()
        
        # 给super_admin角色分配所有权限
        for perm in all_permissions:
            if perm not in super_admin_role.permissions:
                super_admin_role.permissions.append(perm)
        
        # 给admin角色分配管理权限
        admin_perms = [p for p in all_permissions if p.code in ["admin.access", "crawler.read", "crawler.manage", "user.read", "user.create", "user.update", "user.delete"]]
        for perm in admin_perms:
            if perm not in admin_role.permissions:
                admin_role.permissions.append(perm)
        
        db.commit()
        
        # 4. 创建管理员用户
        print("\n创建管理员用户...")
        
        # 检查admin用户是否已存在
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password_hash=hash_password("admin123"),
                first_name="系统",
                last_name="管理员",
                nickname="Admin",
                role=UserRoleEnum.ADMIN,
                status=UserStatusEnum.ACTIVE,
                is_verified=True,
                user_type=UserTypeEnum.ADMIN,
                login_count=0
            )
            db.add(admin_user)
            db.flush()
            print("  创建管理员用户: admin (密码: admin123)")
        else:
            print("  管理员用户已存在: admin")
        
        # 5. 给用户分配角色
        print("\n给用户分配角色...")
        if admin_user:
            # 分配admin角色
            admin_role_obj = db.query(Role).filter(Role.code == "admin").first()
            if admin_role_obj and admin_role_obj not in admin_user.roles:
                admin_user.roles.append(admin_role_obj)
                print("  给用户分配admin角色")
            
            # 同时分配super_admin角色（便于测试）
            super_admin_role_obj = db.query(Role).filter(Role.code == "super_admin").first()
            if super_admin_role_obj and super_admin_role_obj not in admin_user.roles:
                admin_user.roles.append(super_admin_role_obj)
                print("  给用户分配super_admin角色")
        
        db.commit()
        
        print("\n✅ 初始化完成！")
        print("\n登录信息:")
        print("  用户名: admin")
        print("  密码: admin123")
        print("\n现在你可以:")
        print("  1. 重启后端服务")
        print("  2. 用上述账号登录后台管理系统")
        print("  3. 在爬虫配置页面查看 500.com足球竞彩 数据源")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # 检查是否安装了bcrypt
    try:
        import bcrypt
    except ImportError:
        print("❌ 请先安装bcrypt: pip install bcrypt")
        sys.exit(1)
    
    init_admin_data()
