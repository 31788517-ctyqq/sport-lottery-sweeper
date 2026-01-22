"""
同步创建管理员用户的脚本
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir
sys.path.insert(0, str(project_root))

import sqlite3
from backend.core.security import get_password_hash

def create_admin_user():
    """创建管理员用户"""
    # 连接数据库
    conn = sqlite3.connect('sport_lottery.db')
    cursor = conn.cursor()
    
    try:
        # 检查用户是否已存在
        cursor.execute("SELECT username FROM users WHERE username = ?", ("admin",))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print("管理员用户 'admin' 已存在，删除并重新创建...")
            cursor.execute("DELETE FROM users WHERE username = ?", ("admin",))
        
        # 创建管理员用户
        password_hash = get_password_hash("Admin123!@#")
        cursor.execute("""
            INSERT INTO users (
                username, email, password_hash, 
                user_type, status, is_verified, 
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            "admin", 
            "admin@sports-lottery.local", 
            password_hash,
            "admin",
            "active",
            1
        ))
        
        conn.commit()
        print("管理员用户 'admin' 创建成功！密码: Admin123!@#")
        print(f"密码哈希: {password_hash}")
        
    except Exception as e:
        print(f"创建管理员用户时出错: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_admin_user()