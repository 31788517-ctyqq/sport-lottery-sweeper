#!/usr/bin/env python3
import sqlite3

db_path = "data/sport_lottery.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询角色数
    cursor.execute("SELECT COUNT(*) FROM roles")
    role_count = cursor.fetchone()[0]
    print(f"数据库中的角色数: {role_count}")
    
    # 列出所有角色
    cursor.execute("SELECT id, name, level, is_system, status FROM roles ORDER BY level DESC")
    roles = cursor.fetchall()
    
    print("\n角色列表:")
    print("="*80)
    for role in roles:
        role_id, name, level, is_system, status = role
        print(f"ID={role_id} | Name={name} | Level={level} | System={is_system} | Status={status}")
    
    conn.close()
    
except Exception as e:
    print(f"错误: {e}")
