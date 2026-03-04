#!/usr/bin/env python
"""
测试数据库表
"""

import sqlite3
import os
import sys

def main():
    db_path = os.path.join(os.getcwd(), 'data', 'data/sport_lottery.db')
    print(f"数据库路径: {db_path}")
    print(f"文件存在: {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        print("错误: 数据库文件不存在")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print(f"\n数据库中有 {len(tables)} 个表:")
        for table in tables:
            print(f"  - {table[0]}")
            
            # 如果是crawler_tasks或crawler_configs，显示行数
            if table[0] in ['crawler_tasks', 'crawler_configs']:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"    -> 记录数: {count}")
        
        # 特别检查crawler_tasks表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crawler_tasks'")
        if cursor.fetchone():
            print("\n✅ crawler_tasks表存在")
        else:
            print("\n❌ crawler_tasks表不存在")
            
            # 检查crawler_configs表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crawler_configs'")
            if cursor.fetchone():
                print("✅ crawler_configs表存在，可以创建crawler_tasks表")
            else:
                print("❌ crawler_configs表也不存在")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"数据库错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)