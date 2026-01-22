#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import bcrypt

DB_PATH = 'sport_lottery.db'
PASSWORD = 'admin123'

# 生成 bcrypt 哈希
pwd_hash = bcrypt.hashpw(PASSWORD.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode()

# 连接数据库并更新
conn = sqlite3.connect(DB_PATH)
try:
    conn.execute("UPDATE users SET password_hash = ? WHERE username = 'admin'", (pwd_hash,))
    conn.commit()
    print('✅ admin 密码已更新为:', PASSWORD)
finally:
    conn.close()
