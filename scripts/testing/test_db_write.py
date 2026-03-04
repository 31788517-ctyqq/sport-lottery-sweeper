import sqlite3

conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()

# 创建测试表
cursor.execute('CREATE TABLE IF NOT EXISTS test_table (id INTEGER, name TEXT)')

# 插入测试数据
cursor.execute('INSERT INTO test_table VALUES (?, ?)', (1, 'test'))

# 提交事务
conn.commit()

# 查询数据
cursor.execute('SELECT COUNT(*) FROM test_table')
count = cursor.fetchone()[0]
print(f'Test table records: {count}')

# 清理
cursor.execute('DROP TABLE test_table')
conn.commit()
conn.close()

print('Database write test completed successfully!')