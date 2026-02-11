import sqlite3

conn = sqlite3.connect('sport_lottery.db')
cur = conn.cursor()

# 检查数据源总数
cur.execute('SELECT COUNT(*) FROM data_sources')
count = cur.fetchone()[0]
print(f'数据源总数: {count}')

if count > 0:
    # 显示前几条记录
    cur.execute('SELECT id, name, type, status, source_id FROM data_sources LIMIT 5')
    rows = cur.fetchall()
    print('前5条数据:')
    for row in rows:
        print(f'  {row}')
else:
    print('数据源表为空')

conn.close()
