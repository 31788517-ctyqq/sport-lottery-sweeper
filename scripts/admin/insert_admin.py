import sqlite3
import bcrypt
import sys

def insert_admin():
    conn = sqlite3.connect('sport_lottery.db')
    c = conn.cursor()
    
    # 检查是否已存在
    c.execute("SELECT id FROM users WHERE username='admin'")
    if c.fetchone():
        print("admin用户已存在")
        conn.close()
        return True
    
    password = 'admin123'
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # 尝试插入，使用通用列
    try:
        c.execute('''
            INSERT INTO users (username, email, password_hash, role, status, is_verified, is_online, user_type, timezone, language, notification_preferences, login_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        ''', ('admin', 'admin@example.com', password_hash, 'admin', 'active', 1, 0, 'admin', 'UTC', 'zh', '{}', 0))
        conn.commit()
        print("admin用户插入成功")
        return True
    except Exception as e:
        print("插入失败:", e)
        # 尝试获取列信息
        c.execute('PRAGMA table_info(users)')
        cols = c.fetchall()
        print("表列信息:")
        for col in cols:
            print(f"  {col[1]} ({col[2]}) {'NOT NULL' if col[3] else ''}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    success = insert_admin()
    sys.exit(0 if success else 1)