#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新数据库中data_sources表的status列，将整数值转换为字符串值
"""

import sqlite3
import os
from pathlib import Path

# 连接到数据库
db_path = Path(__file__).resolve().parent / 'sport_lottery.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("更新前的status数据:")
cursor.execute("SELECT id, name, status FROM data_sources LIMIT 10;")
rows = cursor.fetchall()
for row in rows:
    print(f"  ID: {row[0]}, Name: {row[1]}, Status: {row[2]} (type: {type(row[2]).__name__})")

# 将整数值转换为字符串值
cursor.execute("""
UPDATE data_sources 
SET status = CASE 
    WHEN status = 1 THEN 'online'
    WHEN status = 0 THEN 'offline' 
    ELSE 'offline'
END
WHERE typeof(status) = 'integer';
""")

conn.commit()

print("\n更新后的status数据:")
cursor.execute("SELECT id, name, status FROM data_sources LIMIT 10;")
rows = cursor.fetchall()
for row in rows:
    print(f"  ID: {row[0]}, Name: {row[1]}, Status: {row[2]} (type: {type(row[2]).__name__})")

conn.close()
print("\n数据库更新完成！")

if __name__ == "__main__":
    update_status_column()