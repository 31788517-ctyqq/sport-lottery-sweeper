#!/usr/bin/env python3
"""
修复roles表结构
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from backend.config import DATABASE_PATH

def main():
    db_path = str(DATABASE_PATH)
    print(f"Database path: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查roles表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='roles'")
    if not cursor.fetchall():
        print("ERROR: roles table does not exist!")
        # 创建表？可能需要运行迁移
        sys.exit(1)
    
    # 检查列
    cursor.execute("PRAGMA table_info(roles)")
    columns = cursor.fetchall()
    print("Current columns:")
    for col in columns:
        print(f"  {col[0]}: {col[1]} ({col[2]})")
    
    # 检查是否缺少permissions列
    col_names = [col[1] for col in columns]
    if 'permissions' not in col_names:
        print("Adding missing 'permissions' column...")
        cursor.execute("ALTER TABLE roles ADD COLUMN permissions TEXT")
        print("Column added.")
    else:
        print("'permissions' column already exists.")
    
    # 检查status列类型（应该是BOOLEAN，但SQLite存储为INTEGER）
    # 不需要修改
    
    # 插入默认角色（如果表为空）
    cursor.execute("SELECT COUNT(*) FROM roles")
    count = cursor.fetchone()[0]
    print(f"Current row count: {count}")
    
    if count == 0:
        print("Inserting default roles...")
        default_roles = [
            ("超级管理员", "系统最高权限管理员，拥有所有权限", "[]", 1, 1),
            ("管理员", "系统管理员，拥有大部分管理权限", "[]", 1, 2),
            ("内容审核员", "负责内容审核和用户管理", "[]", 1, 3),
            ("审计员", "查看系统日志和审计报告", "[]", 1, 4),
            ("运营人员", "数据录入和维护", "[]", 1, 5)
        ]
        for name, desc, perm, status, sort in default_roles:
            cursor.execute("""
                INSERT INTO roles (name, description, permissions, status, sort_order, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (name, desc, perm, status, sort))
        print(f"Inserted {len(default_roles)} default roles.")
    
    conn.commit()
    
    # 验证
    cursor.execute("SELECT id, name, status FROM roles")
    rows = cursor.fetchall()
    print("Roles in table:")
    for row in rows:
        print(f"  {row[0]}: {row[1]} (status: {row[2]})")
    
    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()