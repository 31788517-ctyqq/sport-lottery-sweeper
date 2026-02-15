import sqlite3
import os

# 连接到backend目录下的数据库
backend_db_path = os.path.join(os.getcwd(), 'backend', 'data/sport_lottery.db')
print('Backend DB路径:', backend_db_path)

conn = sqlite3.connect(backend_db_path)
cursor = conn.cursor()

# 检查是否已有source_id列
cursor.execute("PRAGMA table_info(data_sources);")
columns = cursor.fetchall()
column_names = [col[1] for col in columns]

if 'source_id' not in column_names:
    # 添加source_id列
    cursor.execute("ALTER TABLE data_sources ADD COLUMN source_id VARCHAR(10);")
    print("✅ 已添加source_id列到backend数据库")
else:
    print("✅ backend数据库中source_id列已存在")

# 更新现有记录的source_id值
cursor.execute("SELECT id, name FROM data_sources;")
records = cursor.fetchall()
for record in records:
    source_id_value = f"DS{record[0]:03d}"
    cursor.execute("UPDATE data_sources SET source_id = ? WHERE id = ?", (source_id_value, record[0]))
    print(f"  更新 ID {record[0]}: {record[1]} -> {source_id_value}")

conn.commit()
conn.close()
print("✅ backend数据库更新完成！")