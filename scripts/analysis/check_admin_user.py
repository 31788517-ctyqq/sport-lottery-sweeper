#!/usr/bin/env python3
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def check_admin_user():
    from backend.database import engine
    from sqlalchemy.orm import sessionmaker
    from backend.models.admin_user import AdminUser
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        admin_user = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if admin_user:
            print(f"✅ 管理员用户存在:")
            print(f"   用户名: {admin_user.username}")
            print(f"   邮箱: {admin_user.email}")
            print(f"   真实姓名: {admin_user.real_name}")
            print(f"   角色: {admin_user.role}")
            print(f"   状态: {admin_user.status}")
        else:
            print("❌ 管理员用户不存在")
            
    except Exception as e:
        print(f"❌ 查询管理员用户失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_admin_user()
"""
检查数据库中admin用户是否存在
"""
import os
import sqlite3
from pathlib import Path

def check_admin_user():
    # 获取项目根目录
    project_root = Path(__file__).parent
    db_paths = [
        project_root / 'data/sport_lottery.db',
        project_root / 'data' / 'data/sport_lottery.db'
    ]

    db_path = None
    for path in db_paths:
        if path.exists():
            db_path = str(path)
            break

    if db_path:
        print(f'Database found: {db_path}')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        # Check if admin_users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_users';")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print('admin_users table exists')
            # Query for the admin user
            cursor.execute("SELECT id, username, email, role, status FROM admin_users WHERE username = 'admin'")
            admin_user = cursor.fetchone()
            if admin_user:
                print(f'Admin user found: id={admin_user["id"]}, username={admin_user["username"]}, email={admin_user["email"]}, role={admin_user["role"]}, status={admin_user["status"]}')
            else:
                print('No admin user found in database')
                # Let's see what users exist
                cursor.execute("SELECT id, username, email, role, status FROM admin_users")
                all_users = cursor.fetchall()
                if all_users:
                    print('Other users in database:')
                    for user in all_users:
                        print(f'  - id={user["id"]}, username={user["username"]}, email={user["email"]}, role={user["role"]}, status={user["status"]}')
                else:
                    print('No users found in admin_users table')
        else:
            print('admin_users table does not exist')
            # List all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print('Available tables:', [table[0] for table in tables])
        
        conn.close()
    else:
        print('Database not found in expected locations')

if __name__ == "__main__":
    check_admin_user()