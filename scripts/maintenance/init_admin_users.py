#!/usr/bin/env python3
"""
初始化管理员用户脚本
"""
import sqlite3
import bcrypt
import os

# 数据库路径
DB_PATH = "data/sport_lottery.db"

def init_admin_users():
    """初始化管理员用户"""
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建admin_users表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'admin',
        status TEXT DEFAULT 'active'
    )
    ''')
    
    # 创建测试用户
    password = 'admin123'
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # 插入管理员用户
    users = [
        ('admin', 'admin@sportlottery.com', password_hash, 'admin', 'active'),
        ('superadmin', 'superadmin@sportlottery.com', password_hash, 'super_admin', 'active')
    ]
    
    for username, email, pwd_hash, role, status in users:
        cursor.execute('SELECT username FROM admin_users WHERE username = ?', (username,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO admin_users (username, email, password_hash, role, status) 
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, pwd_hash, role, status))
            print(f'Created user: {username}')
    
    conn.commit()
    conn.close()
    print('Database initialized successfully!')

if __name__ == '__main__':
    init_admin_users()
