import sqlite3

conn = sqlite3.connect('sport_lottery.db')
cursor = conn.cursor()

# 检查记录数
cursor.execute('SELECT COUNT(*) FROM football_matches')
count = cursor.fetchone()[0]
print(f'Football matches records: {count}')

# 如果有数据，查看表结构
if count > 0:
    cursor.execute('PRAGMA table_info(football_matches)')
    columns = cursor.fetchall()
    print('Table columns:')
    for col in columns[:10]:  # 只显示前10列
        print(f'- {col[1]} ({col[2]})')
else:
    print('No data in football_matches table')

conn.close()