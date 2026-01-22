"""
直接使用SQLite检查用户数量的脚本
"""

import sqlite3
import os

# 数据库文件路径
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'sport_lottery.db')

def check_users():
    """直接查询用户表"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查users表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # 查询用户总数
            cursor.execute("SELECT COUNT(*) FROM users;")
            total_count = cursor.fetchone()[0]
            print(f"用户总数: {total_count}")
            
            # 查询前5个用户
            if total_count > 0:
                cursor.execute("SELECT username, email, status, user_type FROM users LIMIT 5;")
                users = cursor.fetchall()
                print("\n前5个用户:")
                for i, user in enumerate(users):
                    print(f"{i+1}. 用户名: {user[0]}, 邮箱: {user[1]}, 状态: {user[2]}, 类型: {user[3]}")
        else:
            print("users表不存在")
            
        conn.close()
    except Exception as e:
        print(f"查询出错: {e}")

if __name__ == "__main__":
    check_users()