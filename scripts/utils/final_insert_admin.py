#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = 'data/sport_lottery.db'

# MD5('admin123') = 0192023a7bbd73250516f069df18b500
PWD_HASH = '0192023a7bbd73250516f069df18b500'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("""
        INSERT OR IGNORE INTO users 
        (username, email, password_hash, first_name, last_name, nickname, role, status, is_verified, user_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('admin', 'admin@example.com', PWD_HASH, '系统', '管理员', 'Admin', 'admin', 'active', 1, 'admin'))
    conn.commit()
    print("✅ admin用户插入成功 (或用已存在)")
except Exception as e:
    conn.rollback()
    print(f"❌ 插入失败: {e}")
finally:
    conn.close()
