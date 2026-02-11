import sqlite3

conn = sqlite3.connect('sport_lottery.db')
cursor = conn.cursor()

# 查找包含100或ball的表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%100%' OR name LIKE '%ball%')")
tables = cursor.fetchall()
print('Tables containing "100" or "ball":')
for table in tables:
    print(f'- {table[0]}')

conn.close()