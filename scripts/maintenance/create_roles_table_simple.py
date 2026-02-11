#!/usr/bin/env python3
import sqlite3
import sys

def main():
    db_path = "sport_lottery.db"
    
    # SQL创建roles表（根据backend/models/role.py定义）
    create_sql = """
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        permissions TEXT,
        status BOOLEAN NOT NULL DEFAULT 1,
        sort_order INTEGER NOT NULL DEFAULT 0,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # 创建索引
    index_sql1 = "CREATE INDEX IF NOT EXISTS ix_roles_name ON roles (name);"
    index_sql2 = "CREATE INDEX IF NOT EXISTS ix_roles_status ON roles (status);"
    unique_sql = "CREATE UNIQUE INDEX IF NOT EXISTS uq_roles_name ON roles (name);"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='roles'")
        if cursor.fetchone():
            print("✓ 'roles' table already exists")
        else:
            print("Creating 'roles' table...")
            cursor.execute(create_sql)
            cursor.execute(index_sql1)
            cursor.execute(index_sql2)
            cursor.execute(unique_sql)
            conn.commit()
            print("✓ 'roles' table created successfully")
        
        # 验证表结构
        cursor.execute("PRAGMA table_info(roles)")
        columns = cursor.fetchall()
        print("\nTable structure:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} ({col[2]}) {'NOT NULL' if col[3] else ''} {'PK' if col[5] else ''}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()