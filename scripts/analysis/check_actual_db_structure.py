import sqlite3

# 连接到SQLite数据库
conn = sqlite3.connect('backend/data/main.db')
cursor = conn.cursor()

# 检查crawler_configs表结构
print("crawler_configs表结构:")
cursor.execute("PRAGMA table_info(crawler_configs);")
rows = cursor.fetchall()
for row in rows:
    cid, name, type_, notnull, default_value, pk = row
    print(f"  {name}: {type_} (not null: {bool(notnull)}, pk: {bool(pk)})")

print("\n尝试执行UPDATE语句测试:")
try:
    # 尝试执行一个简单的更新操作
    cursor.execute("UPDATE crawler_configs SET source_id=? WHERE source_id=?", (None, 999))
    print("  ✓ UPDATE语句可以执行")
except sqlite3.Error as e:
    print(f"  × UPDATE语句执行失败: {e}")

conn.close()