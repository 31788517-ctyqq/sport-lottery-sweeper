#!/usr/bin/env python3
"""
检查数据源表的实际结构
"""

import sys
import os
import sqlite3
from pathlib import Path

def check_data_source_table():
    """检查数据源表结构"""
    try:
        # 使用项目根目录下的数据库文件
        project_root = Path(__file__).parent
        db_path = project_root / "sport_lottery.db"
        
        if not db_path.exists():
            print(f"数据库文件不存在: {db_path}")
            return
        
        # 连接到SQLite数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print(f"检查数据库表结构: {db_path}")
        print("=" * 60)
        
        # 检查data_sources表的结构
        print("检查data_sources表的列结构:")
        cursor.execute("PRAGMA table_info(data_sources);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  列ID: {col[0]}, 名称: {col[1]}, 类型: {col[2]}, 非空: {col[3]}, 默认值: {col[4]}, 主键: {col[5]}")
        
        print("-" * 60)
        
        # 检查最新创建的数据源记录
        cursor.execute("SELECT * FROM data_sources ORDER BY id DESC LIMIT 5;")
        records = cursor.fetchall()
        print("最近的数据源记录:")
        for record in records:
            print(f"  ID: {record[0]}, Name: {record[1]}")
            # 打印所有字段
            for i, val in enumerate(record):
                print(f"    列{i}: {columns[i][1]} = {val}")
            print()
        
        conn.close()
                
    except Exception as e:
        print(f"检查数据库结构时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_data_source_table()