"""
检查sport_lottery.db中的所有数据源相关表
"""
import sqlite3
import os

# 数据库文件路径
db_path = "backend/database.db"

# 连接到SQLite数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查数据库中的所有表
print("数据库中的所有表:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")

conn.close()
print("\n数据库表检查完成")


def check_all_tables():
    conn = sqlite3.connect('data/sport_lottery.db')
    cursor = conn.cursor()

    # 查询数据库中所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('数据库表列表:', [table[0] for table in tables])

    # 尝试查询可能的数据源相关表
    possible_tables = ['sources', 'crawler_sources', 'data_sources', 'crawler_configs']
    for table in possible_tables:
        print(f'\n=== {table} 表数据 ===')
        try:
            cursor.execute(f'SELECT * FROM {table};')
            rows = cursor.fetchall()
            for row in rows:
                print(row)
        except sqlite3.OperationalError as e:
            print(f'Error accessing {table} table: {e}')

    conn.close()

if __name__ == "__main__":
    check_all_tables()