import sqlite3

conn = sqlite3.connect('sport_lottery.db')
cursor = conn.cursor()

# 查找包含sp的表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%sp%'")
tables = cursor.fetchall()
print('SP tables:')
for table in tables:
    print(f'- {table[0]}')
    
    # 检查数据量
    cursor.execute(f'SELECT COUNT(*) FROM {table[0]}')
    count = cursor.fetchone()[0]
    print(f'  Records: {count}')

conn.close()