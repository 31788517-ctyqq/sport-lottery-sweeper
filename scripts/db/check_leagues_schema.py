#!/usr/bin/env python3
import sqlite3
import sys

DB_PATH = 'sport_lottery.db'

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(leagues)")
    columns = cursor.fetchall()
    if not columns:
        print("❌ leagues 表不存在或为空")
        sys.exit(1)
    print("📋 leagues 表结构：")
    for col in columns:
        print(f"{col[1]} ({col[2]})")
    conn.close()
except Exception as e:
    print(f"❌ 读取表结构出错: {e}")
    sys.exit(1)
