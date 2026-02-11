import sqlite3
import os

# 检查当前目录下的sport_lottery.db文件
db_path = os.path.join(os.getcwd(), 'sport_lottery.db')
print('数据库路径:', db_path)
print('文件是否存在:', os.path.exists(db_path))

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('数据库中的表:', [table[0] for table in tables])
    
    if 'data_sources' in [table[0] for table in tables]:
        # 查询数据源记录
        cursor.execute('SELECT id, name, source_id FROM data_sources;')
        records = cursor.fetchall()
        print('数据源记录:')
        for record in records:
            print(f'  ID: {record[0]}, Name: {record[1]}, Source ID: {record[2]}')
    
    conn.close()
else:
    print('数据库文件不存在')