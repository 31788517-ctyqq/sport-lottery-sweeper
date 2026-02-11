#!/usr/bin/env python3
import sys
import os
import sqlite3

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def check_user_fields():
    # 直接查询数据库
    conn = sqlite3.connect('sport_lottery.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, department, position FROM admin_users WHERE username = 'admin'")
    result = cursor.fetchone()
    conn.close()
    
    if result:
        username, department, position = result
        print(f"用户名: {username}")
        print(f"部门: {department}")
        print(f"职位: {position}")
    else:
        print("❌ 未找到管理员用户")

if __name__ == "__main__":
    check_user_fields()