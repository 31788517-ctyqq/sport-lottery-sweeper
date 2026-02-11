#!/usr/bin/env python3
"""
验证roles表结构和数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from backend.config import DATABASE_PATH

def main():
    db_path = str(DATABASE_PATH)
    print(f"Database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='roles'")
    if not cursor.fetchall():
        print("ERROR: roles table does not exist!")
        sys.exit(1)
    
    # 获取列信息
    cursor.execute("PRAGMA table_info(roles)")
    cols = cursor.fetchall()
    print("\nTable columns:")
    for col in cols:
        print(f"  {col[0]}: {col[1]} ({col[2]})")
    
    # 检查是否有数据
    cursor.execute("SELECT COUNT(*) FROM roles")
    count = cursor.fetchone()[0]
    print(f"\nRow count: {count}")
    
    if count == 0:
        print("Inserting default roles...")
        default = [
            ("超级管理员", "系统最高权限管理员，拥有所有权限", "[]", 1, 1),
            ("管理员", "系统管理员，拥有大部分管理权限", "[]", 1, 2),
            ("内容审核员", "负责内容审核和用户管理", "[]", 1, 3),
            ("审计员", "查看系统日志和审计报告", "[]", 1, 4),
            ("运营人员", "数据录入和维护", "[]", 1, 5)
        ]
        for name, desc, perm, status, sort in default:
            cursor.execute("""
                INSERT INTO roles (name, description, permissions, status, sort_order, 
                                   created_at, updated_at, is_deleted, deleted_at, 
                                   created_by, updated_by, deleted_by)
                VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'), 
                        0, NULL, NULL, NULL, NULL)
            """, (name, desc, perm, status, sort))
        conn.commit()
        print("Default roles inserted.")
    
    # 显示数据
    cursor.execute("SELECT id, name, status, permissions FROM roles")
    rows = cursor.fetchall()
    print("\nRoles:")
    for row in rows:
        print(f"  {row[0]}: {row[1]} (status: {row[2]}, permissions: {row[3]})")
    
    conn.close()
    print("\nVerification complete.")

if __name__ == "__main__":
    main()