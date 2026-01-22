#!/usr/bin/env python3
import sys
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir
sys.path.insert(0, str(project_root))

import sqlite3
from datetime import datetime
from backend.core.security import get_password_hash

def create_proper_admin_user():
    db_path = "sport_lottery.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== 创建正确的管理员用户 ===")
    
    # 首先检查表是否存在，如果不存在则创建
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_users';")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        print("admin_users表不存在，需要创建...")
        # 这里应该创建完整的表结构，但为了简单起见，我们假设表已存在
        print("请先运行数据库迁移来创建正确的表结构")
        conn.close()
        return
    
    # 检查是否已存在admin用户
    cursor.execute("SELECT id FROM admin_users WHERE username = ?", ("admin",))
    existing = cursor.fetchone()
    
    if existing:
        print(f"admin用户已存在，ID: {existing[0]}")
        # 更新密码
        password_hash = get_password_hash("admin123")
        cursor.execute("""
            UPDATE admin_users 
            SET password_hash = ?, 
                status = 'active',
                role = 'admin',
                is_verified = 1,
                must_change_password = 0,
                real_name = '系统管理员',
                email = 'admin@example.com',
                updated_at = datetime('now')
            WHERE username = ?
        """, (password_hash, "admin"))
        print(f"已更新admin用户密码")
    else:
        # 创建新的admin用户
        password_hash = get_password_hash("admin123")
        current_time = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO admin_users (
                username, email, password_hash, real_name,
                role, status, is_verified, must_change_password,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "admin",
            "admin@example.com",
            password_hash,
            "系统管理员",
            "admin",
            "active",
            1,  # is_verified
            0,  # must_change_password
            current_time,
            current_time
        ))
        print(f"已创建admin用户")
    
    conn.commit()
    
    # 验证
    cursor.execute("SELECT username, email, role, status FROM admin_users WHERE username = 'admin';")
    user = cursor.fetchone()
    if user:
        print(f"\n验证创建的用户:")
        print(f"  用户名: {user[0]}")
        print(f"  邮箱: {user[1]}")
        print(f"  角色: {user[2]}")
        print(f"  状态: {user[3]}")
        print(f"  密码: admin123")
    else:
        print("\n创建失败: 用户未找到")
    
    # 显示所有admin用户
    cursor.execute("SELECT username, email, role, status FROM admin_users ORDER BY id;")
    users = cursor.fetchall()
    print(f"\nadmin_users表中的所有用户 ({len(users)} 个):")
    for u in users:
        print(f"  - {u[0]} ({u[1]}), 角色: {u[2]}, 状态: {u[3]}")
    
    conn.close()
    print("\n=== 完成 ===")

if __name__ == "__main__":
    create_proper_admin_user()