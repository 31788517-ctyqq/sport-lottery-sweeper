#!/usr/bin/env python3
"""
测试数据库连接和admin用户
"""
import sys
sys.path.insert(0, '.')

from backend.core.database import SessionLocal
from backend.models.admin_user import AdminUser, AdminStatusEnum, AdminRoleEnum
from sqlalchemy import inspect

def test_db():
    print("=== 测试数据库连接 ===")
    session = SessionLocal()
    try:
        # 检查表是否存在
        inspector = inspect(session.bind)
        tables = inspector.get_table_names()
        print(f"数据库中的表 ({len(tables)}):")
        for table in tables:
            print(f"  - {table}")
        
        # 检查 admin_users 表
        if 'admin_users' in tables:
            print("\n检查 admin_users 表...")
            columns = inspector.get_columns('admin_users')
            print(f"列 ({len(columns)}):")
            for col in columns:
                print(f"  - {col['name']} ({col['type']})")
            
            # 查询 admin 用户
            admin = session.query(AdminUser).filter(AdminUser.username == 'admin').first()
            if admin:
                print(f"\n找到 admin 用户:")
                print(f"  ID: {admin.id}")
                print(f"  用户名: {admin.username}")
                print(f"  邮箱: {admin.email}")
                print(f"  角色: {admin.role}")
                print(f"  状态: {admin.status}")
                print(f"  密码哈希: {admin.password_hash[:20]}...")
                print(f"  登录次数: {admin.login_count}")
            else:
                print("\n未找到 admin 用户！")
                # 列出所有用户
                users = session.query(AdminUser).all()
                print(f"总用户数: {len(users)}")
                for u in users:
                    print(f"  - {u.id}: {u.username} ({u.email})")
        else:
            print("\nadmin_users 表不存在！")
            
    except Exception as e:
        print(f"数据库错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    test_db()