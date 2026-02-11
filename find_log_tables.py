import sqlite3

conn = sqlite3.connect('sport_lottery.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%log%' OR name LIKE '%admin%')")
log_tables = cursor.fetchall()

print('Log-related tables:')
for table in log_tables:
    print(f'- {table[0]}')
    
    # 检查数据量
    cursor.execute(f'SELECT COUNT(*) FROM {table[0]}')
    count = cursor.fetchone()[0]
    print(f'  Records: {count}')

conn.close()