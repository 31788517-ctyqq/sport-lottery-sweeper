#!/usr/bin/env python3
import sys
import os
import sqlite3

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def check_password_hash():
    # 直接查询数据库
    conn = sqlite3.connect('data/sport_lottery.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, password_hash FROM admin_users WHERE username = 'admin'")
    result = cursor.fetchone()
    conn.close()
    
    if result:
        username, password_hash = result
        print(f"用户名: {username}")
        print(f"数据库中的密码哈希: {password_hash}")
        
        # 验证密码
        from backend.core.security import verify_password
        is_valid = verify_password("admin123", password_hash)
        print(f"密码验证结果: {is_valid}")
    else:
        print("❌ 未找到管理员用户")

if __name__ == "__main__":
    check_password_hash()