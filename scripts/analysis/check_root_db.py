#!/usr/bin/env python
"""
检查根目录数据库
"""

import sqlite3
import os

def main():
    db_path = 'data/sport_lottery.db'
    print(f"检查数据库: {db_path}")
    print(f"文件大小: {os.path.getsize(db_path) if os.path.exists(db_path) else '不存在'} 字节")
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"\n📋 数据库中有 {len(tables)} 个表:")
    for table in tables:
        print(f"  - {table[0]}")
        
        # 如果是我们关心的表，显示行数
        if table[0] in ['crawler_tasks', 'crawler_configs', 'admin_users', 'matches']:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"    -> 记录数: {count}")
            
            # 显示前几条记录
            if count > 0 and table[0] == 'crawler_configs':
                cursor.execute(f"SELECT id, name, url FROM {table[0]} LIMIT 5")
                for row in cursor.fetchall():
                    print(f"      ID {row[0]}: {row[1]} - {row[2]}")
    
    # 特别检查
    print("\n🔍 特别检查:")
    
    # crawler_tasks表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crawler_tasks'")
    if cursor.fetchone():
        print("✅ crawler_tasks表存在")
    else:
        print("❌ crawler_tasks表不存在")
    
    # crawler_configs表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crawler_configs'")
    if cursor.fetchone():
        print("✅ crawler_configs表存在")
    else:
        print("❌ crawler_configs表不存在")
    
    # 检查是否有外键约束问题
    cursor.execute("PRAGMA foreign_keys")
    fk_enabled = cursor.fetchone()[0]
    print(f"外键约束: {'启用' if fk_enabled else '禁用'}")
    
    conn.close()
    return True

if __name__ == "__main__":
    main()