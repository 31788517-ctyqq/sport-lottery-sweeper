import sys
import os
sys.path.insert(0, 'backend')

from core.database import create_tables, Base, engine
import sqlite3

print("创建数据库表...")
create_tables()
print("✅ 表创建完成")

# 列出表
conn = sqlite3.connect('data/sport_lottery.db')
c = conn.cursor()
c.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = c.fetchall()
print(f"现有表: {tables}")