import sqlite3

conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()

# 检查记录数
cursor.execute('SELECT COUNT(*) FROM ip_pools')
count = cursor.fetchone()[0]
print(f'IP pools records: {count}')

# 如果有数据，查看详细信息
if count > 0:
    # 获取列名
    cursor.execute('PRAGMA table_info(ip_pools)')
    columns_info = cursor.fetchall()
    column_names = [col[1] for col in columns_info]
    print('Column names:', column_names)
    
    # 查看前几条记录
    cursor.execute('SELECT * FROM ip_pools LIMIT 3')
    rows = cursor.fetchall()
    for i, row in enumerate(rows):
        print(f'Record {i+1}:')
        for j, value in enumerate(row):
            print(f'  {column_names[j]}: {value}')
else:
    print('No data in ip_pools table')

conn.close()