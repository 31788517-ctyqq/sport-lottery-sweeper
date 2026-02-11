#!/usr/bin/env python3
import sys
import os
import sqlite3

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def check_user_status():
    # 直接查询数据库
    conn = sqlite3.connect('sport_lottery.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, status FROM admin_users WHERE username = 'admin'")
    result = cursor.fetchone()
    conn.close()
    
    if result:
        username, status = result
        print(f"用户名: {username}")
        print(f"数据库中的状态: {status}")
        
        # 检查状态是否为active
        from backend.models.admin_user import AdminStatusEnum
        is_active = status == AdminStatusEnum.ACTIVE.value
        print(f"状态是否为active: {is_active}")
    else:
        print("❌ 未找到管理员用户")

if __name__ == "__main__":
    check_user_status()