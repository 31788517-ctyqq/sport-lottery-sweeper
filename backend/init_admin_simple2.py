#!/usr/bin/env python3
"""
简单管理员初始化脚本 - 不依赖完整模型导入
"""

import sys
import os
import sqlite3
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.core.security import get_password_hash

def init_admin_user():
    """初始化管理员用户 - 直接操作数据库"""
    try:
        # 使用项目配置的数据库路径
        db_path = os.path.join(project_root, "sport_lottery.db")
        print(f"数据库路径: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查admin_users表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='admin_users';
        """)
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ admin_users表不存在，请先运行数据库迁移")
            conn.close()
            return
        
        # 检查是否已存在管理员用户
        cursor.execute("SELECT id, username FROM admin_users WHERE username = ?", ("admin",))
        existing_admin = cursor.fetchone()
        
        if existing_admin:
            print(f"✅ 管理员用户已存在: ID {existing_admin[0]}, 用户名 {existing_admin[1]}")
        else:
            # 创建超级管理员用户
            now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            password_hash = get_password_hash('admin123')
            
            cursor.execute("""
                INSERT INTO admin_users (
                    username, email, password_hash, real_name, role, status, 
                    is_verified, created_at, updated_at, login_count, department, position,
                    two_factor_enabled, must_change_password, failed_login_attempts,
                    preferences
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                'admin',                    # username
                'admin@example.com',        # email
                password_hash,              # password_hash
                '系统管理员',                 # real_name
                'super_admin',              # role
                'active',                   # status
                1,                          # is_verified
                now,                        # created_at
                now,                        # updated_at
                0,                          # login_count
                '系统管理部',                 # department
                '系统管理员',                 # position
                0,                          # two_factor_enabled (默认不启用)
                0,                          # must_change_password (不需要强制改密码)
                0,                          # failed_login_attempts
                '{}'                        # preferences (空JSON)
            ))
            
            conn.commit()
            print("✅ 管理员用户创建成功!")
        
        print("\n📝 登录信息:")
        print("   用户名: admin")
        print("   密码: admin123")
        print("   提示: 请在前端使用这些凭据登录")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    init_admin_user()