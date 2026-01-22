#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import bcrypt

# 添加backend到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

import sqlite3

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def main():
    DB_PATH = 'sport_lottery.db'
    NEW_PWD = 'admin123'
    NEW_HASH = hash_password(NEW_PWD)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE users SET password_hash = ? WHERE username = 'admin'", (NEW_HASH,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"✅ admin用户密码已更新为: {NEW_PWD}")
        else:
            print("❌ 未找到admin用户")
    except Exception as e:
        conn.rollback()
        print(f"❌ 更新失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
