import sqlite3

conn = sqlite3.connect('sport_lottery.db')
cursor = conn.cursor()

# 检查leagues表总记录数
cursor.execute('SELECT COUNT(*) FROM leagues')
total_count = cursor.fetchone()[0]
print(f'Total leagues records: {total_count}')

# 检查是否有任何记录
if total_count > 0:
    cursor.execute('SELECT name, is_deleted, created_at FROM leagues LIMIT 3')
    rows = cursor.fetchall()
    for row in rows:
        print(f'Name: {row[0]}, Deleted: {row[1]}, Created: {row[2]}')

conn.close()

