import sqlite3
import os

# 数据库文件路径
db_path = "data/sport_lottery.db"

# 连接到SQLite数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查数据库中的所有表
print("数据库中的所有表:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")

# 检查crawler_configs表结构
print("\ncrawler_configs表结构:")
cursor.execute("PRAGMA table_info(crawler_configs);")
rows = cursor.fetchall()
for row in rows:
    cid, name, type_, notnull, default_value, pk = row
    print(f"  {name}: {type_} (not null: {bool(notnull)}, pk: {bool(pk)})")

# 检查是否已有source_id列
has_source_id = any(row[1] == 'source_id' for row in rows)
if has_source_id:
    print("\n✓ crawler_configs表已包含source_id列")
else:
    print("\n× crawler_configs表缺少source_id列，正在添加...")
    try:
        # 添加source_id列
        cursor.execute("ALTER TABLE crawler_configs ADD COLUMN source_id INTEGER;")
        conn.commit()
        print("✓ 成功添加source_id列到crawler_configs表")
    except sqlite3.Error as e:
        print(f"× 添加source_id列失败: {e}")

conn.close()
print("\n数据库结构检查完成")