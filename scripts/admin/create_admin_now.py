#!/usr/bin/env python
"""
立即创建admin用户
"""
import sqlite3
import bcrypt
from datetime import datetime

def main():
    print("正在创建admin用户...")
    
    conn = sqlite3.connect('sport_lottery.db')
    c = conn.cursor()
    
    # 删除旧admin用户（如果存在）
    c.execute("DELETE FROM users WHERE username='admin'")
    
    # 获取当前时间
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 创建新admin用户 - 使用正确的字段
    password = 'admin123'
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        c.execute('''
            INSERT INTO users (username, email, password_hash, first_name, last_name, nickname, 
                              role, status, is_verified, is_online, user_type, timezone, language, 
                              notification_preferences, config, login_count, followers_count, following_count,
                              created_at, updated_at, created_by, updated_by, deleted_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@example.com', password_hash, '系统', '管理员', 'Admin', 
              'admin', 'active', 1, 0, 'admin', 'UTC', 'zh', '{}', '{}', 0, 0, 0,
              current_time, current_time, None, None, None))
        
        conn.commit()
        print("✅ admin用户创建成功!")
        print("   用户名: admin")
        print("   密码: admin123")
        
        # 验证
        c.execute("SELECT username, role, status FROM users WHERE username='admin'")
        row = c.fetchone()
        print(f"   验证: {row}")
        
    except Exception as e:
        print(f"❌ 创建admin用户失败: {e}")
        conn.rollback()
    
    conn.close()

if __name__ == "__main__":
    main()