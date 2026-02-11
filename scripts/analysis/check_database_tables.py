"""
检查数据库表是否已创建
"""
import sqlite3
import os

def main():
    db_path = 'sport_lottery.db'
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    print(f"连接到数据库: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("数据库中存在的表:")
    for i, (table,) in enumerate(tables, 1):
        print(f"{i}. {table}")
    
    print("\n检查特定表是否存在:")
    required_tables = ['request_headers', 'ip_pools']
    
    for table in required_tables:
        exists = any(t[0] == table for t in tables)
        if exists:
            print(f"✅ {table} - 已存在")
        else:
            print(f"❌ {table} - 不存在")
    
    conn.close()

if __name__ == "__main__":
    main()