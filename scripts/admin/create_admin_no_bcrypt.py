#!/usr/bin/env python
"""
创建admin用户（不使用bcrypt，使用简单哈希）
"""
import sqlite3
import hashlib

def main():
    print("正在创建admin用户（简单哈希版本）...")
    
    conn = sqlite3.connect('sport_lottery.db')
    c = conn.cursor()
    
    # 确保users表存在
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password_hash TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            nickname TEXT,
            role TEXT DEFAULT 'normal',
            status TEXT DEFAULT 'active',
            is_verified BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            user_type TEXT DEFAULT 'normal',
            login_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 删除旧admin用户（如果存在）
    c.execute("DELETE FROM users WHERE username='admin'")
    
    # 创建新admin用户 - 使用简单哈希（仅用于测试）
    password = 'admin123'
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    try:
        c.execute('''
            INSERT INTO users (username, email, password_hash, first_name, last_name, nickname, 
                              role, status, is_verified, is_active, user_type, login_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@example.com', password_hash, '系统', '管理员', 'Admin', 
              'admin', 'active', 1, 1, 'admin', 0))
        
        conn.commit()
        print("✅ admin用户创建成功!")
        print("   用户名: admin")
        print("   密码: admin123")
        
        # 验证
        c.execute("SELECT username, role, status FROM users WHERE username='admin'")
        row = c.fetchone()
        print(f"   验证: {row}")
        
        # 检查总用户数
        c.execute("SELECT COUNT(*) FROM users")
        count = c.fetchone()[0]
        print(f"   总用户数: {count}")
        
    except Exception as e:
        print(f"❌ 创建admin用户失败: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    
    conn.close()

if __name__ == "__main__":
    main()