import sqlite3
from backend.database import engine
from sqlalchemy import inspect

# 使用SQLAlchemy的inspect功能检查表结构
inspector = inspect(engine)

# 获取crawler_configs表的所有列
columns = inspector.get_columns('crawler_configs')
print("crawler_configs表结构:")
for col in columns:
    print(f"  {col['name']}: {col['type']} (nullable: {col['nullable']})")

print("\n检查数据库中是否存在crawler_configs表...")
try:
    conn = sqlite3.connect('backend/data/main.db')
    cursor = conn.cursor()
    
    # 查询表结构
    cursor.execute("PRAGMA table_info(crawler_configs);")
    rows = cursor.fetchall()
    
    print("crawler_configs表结构 (SQLite PRAGMA):")
    for row in rows:
        cid, name, type_, notnull, default_value, pk = row
        print(f"  {name}: {type_} (not null: {bool(notnull)}, pk: {bool(pk)})")
        
    conn.close()
except Exception as e:
    print(f"连接数据库失败: {e}")