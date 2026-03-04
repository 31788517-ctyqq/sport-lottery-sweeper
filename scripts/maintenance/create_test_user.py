"""
创建测试用户脚本
用于创建一个测试用户以便进行API测试
"""
import sqlite3
import bcrypt
import os
from datetime import datetime

# 获取数据库路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "data/sport_lottery.db")

def create_test_user():
    # 创建密码哈希
    password = "test123"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # 连接到数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 插入一个测试用户
        cursor.execute("""
            INSERT OR IGNORE INTO admin_users (username, email, password_hash, role, status, login_count, department_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "testadmin", 
            "test@example.com", 
            password_hash, 
            "admin",  # role
            "active",  # status
            0,  # login_count
            None  # department_id
        ))
        
        conn.commit()
        
        print("✅ 测试管理员用户创建成功!")
        print(f"用户名: testadmin")
        print(f"密码: test123")
        print(f"数据库路径: {DB_PATH}")
        
        # 验证用户是否创建成功
        cursor.execute("SELECT id, username, role, status FROM admin_users WHERE username = ?", ("testadmin",))
        user = cursor.fetchone()
        
        if user:
            print(f"✅ 用户验证成功: ID={user[0]}, Username={user[1]}, Role={user[2]}, Status={user[3]}")
        else:
            print("❌ 用户未找到")
        
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    create_test_user()