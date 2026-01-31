import sqlite3
import bcrypt
import os
from datetime import datetime

# 获取数据库路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "sport_lottery.db")

def create_admin_user():
    # 创建密码哈希
    password = "admin123"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # 连接到数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 查询admin_users表的结构
        cursor.execute("PRAGMA table_info(admin_users)")
        columns = cursor.fetchall()
        print("admin_users表结构:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - {'' if col[5] == 0 else 'NOT NULL'}")
        
        # 尝试插入一个测试管理员用户
        # 注意：我们需要使用admin_users表，而不是users表
        cursor.execute("""
            INSERT OR IGNORE INTO admin_users (username, email, password_hash, role, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "admin", 
            "admin@example.com", 
            password_hash, 
            "admin",  # role
            "active",  # status
            datetime.now(), 
            datetime.now()
        ))
        
        conn.commit()
        
        print("\n✅ 管理员用户创建成功!")
        print(f"用户名: admin")
        print(f"密码: admin123")
        print(f"数据库路径: {DB_PATH}")
        
        # 验证用户是否创建成功
        cursor.execute("SELECT id, username, role, status FROM admin_users WHERE username = ?", ("admin",))
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
    create_admin_user()