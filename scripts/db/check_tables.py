import sqlite3

def check_tables():
    conn = sqlite3.connect('sport_lottery.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("数据库中的表:")
    for table in tables:
        print(f"  - {table[0]}")
    conn.close()

if __name__ == "__main__":
    check_tables()

import sqlite3
import os

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))
test_db_path = os.path.join(project_root, "sport_lottery_test.db")

print(f"Checking database at: {test_db_path}")
print(f"Database exists: {os.path.exists(test_db_path)}")

if os.path.exists(test_db_path):
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables in database: {tables}")
    conn.close()
else:
    print("Database file does not exist!")

DB_PATH = 'sport_lottery.db'

if not os.path.exists(DB_PATH):
    print(f"数据库文件不存在: {DB_PATH}")
    exit(1)

print(f"数据库文件大小: {os.path.getsize(DB_PATH)} 字节")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 获取所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"\n现有表 ({len(tables)} 个):")
for table in tables:
    table_name = table[0]
    print(f"\n表: {table_name}")
    
    # 获取表结构
    cursor.execute(f"PRAGMA table_info({table_name})")
    cols = cursor.fetchall()
    print(f"  列 ({len(cols)} 个):")
    for col in cols:
        col_id, col_name, col_type, not_null, default_val, pk = col
        pk_str = " PRIMARY KEY" if pk else ""
        not_null_str = " NOT NULL" if not_null else ""
        default_str = f" DEFAULT {default_val}" if default_val else ""
        print(f"    {col_id}: {col_name} {col_type}{not_null_str}{default_str}{pk_str}")
    
    # 获取行数
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  行数: {count}")
    except:
        print(f"  行数: 无法查询")

conn.close()