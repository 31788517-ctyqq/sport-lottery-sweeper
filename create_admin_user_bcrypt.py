import sqlite3
import bcrypt
from datetime import datetime

def create_admin_user():
    # 数据库路径
    # AI_WORKING: coder1 @2026-01-26 - 修正数据库路径，使用根目录下的sport_lottery.db
    db_path = "sport_lottery.db"
    
    # 创建连接
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 为admin用户设置信息
    username = "admin"
    email = "admin@example.com"
    # 密码 "admin123" 
    password_plaintext = "admin123"
    # 使用bcrypt哈希（与后端相同的哈希算法）
    password_hash = bcrypt.hashpw(password_plaintext.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    status = "active"
    user_type = "admin"
    
    try:
        # 删除已存在的admin用户
        cursor.execute("DELETE FROM users WHERE username = ? OR email = ?", (username, email))
        
        # 插入admin用户
        cursor.execute("""
            INSERT INTO users (username, email, hashed_password, status, user_type, is_active, is_verified, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username, 
            email, 
            password_hash, 
            status, 
            user_type, 
            1,  # is_active
            1,  # is_verified
            datetime.now().isoformat(),  # created_at
            datetime.now().isoformat()   # updated_at
        ))
        
        conn.commit()
        print(f"✅ 成功创建管理员用户: {username}")
        print(f"邮箱: {email}")
        print(f"密码: {password_plaintext}")
        print(f"类型: {user_type}")
        print(f"密码哈希: {password_hash[:30]}...")  # 显示部分哈希值
        
    except Exception as e:
        print(f"❌ 创建用户失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_admin_user()