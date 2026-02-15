#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='roles'")
if cursor.fetchone():
    print("roles table exists")
    cursor.execute("PRAGMA table_info(roles)")
    for col in cursor.fetchall():
        print(col)
else:
    print("roles table missing")
conn.close()