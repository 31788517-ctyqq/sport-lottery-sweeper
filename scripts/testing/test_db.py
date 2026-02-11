#!/usr/bin/env python3
import sqlite3
import sys
import os

db_path = os.path.join(os.path.dirname(__file__), 'sport_lottery.db')
print(f'Database path: {db_path}')
print(f'Exists: {os.path.exists(db_path)}')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()
print(f'Total tables: {len(tables)}')
for table in tables:
    print(f'  {table[0]}')
    # 检查列
    cursor.execute(f'PRAGMA table_info({table[0]});')
    cols = cursor.fetchall()
    for col in cols:
        print(f'    {col[1]} ({col[2]})')
    # 检查行数
    cursor.execute(f'SELECT COUNT(*) FROM {table[0]};')
    count = cursor.fetchone()[0]
    print(f'    Rows: {count}')
    if table[0] == 'admin_users':
        cursor.execute(f'SELECT * FROM {table[0]} LIMIT 5;')
        rows = cursor.fetchall()
        for row in rows:
            print(f'      {row}')
conn.close()
print('Done.')