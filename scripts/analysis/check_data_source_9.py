import sqlite3

# 连接数据库
conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()

# 查询ID为9的数据源
cursor.execute("SELECT id, name, url, type FROM data_sources WHERE id = 9")
result = cursor.fetchone()
print('数据源9:', result)

# 查询所有100qiu相关的数据源
cursor.execute("SELECT id, name, url, type FROM data_sources WHERE url LIKE '%100qiu%'")
results = cursor.fetchall()
print('\n所有100qiu数据源:')
for r in results:
    print(f'  {r}')

conn.close()