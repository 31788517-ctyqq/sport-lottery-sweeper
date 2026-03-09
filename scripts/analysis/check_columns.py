#!/usr/bin/env python3
"""
检查数据库表结构
"""

import sqlite3
from pathlib import Path

def check_columns():
    """检查数据库表结构"""
    try:
        # 使用项目根目录下的数据库文件
        project_root = Path(__file__).parent
        db_path = project_root / "data/sport_lottery.db"
        
        if not db_path.exists():
            print(f"数据库文件不存在: {db_path}")
            return
        
        # 连接到SQLite数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("检查data_sources表结构:")
        cursor.execute("PRAGMA table_info(data_sources);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - {'主键' if col[5] else ''}")
        
        print("\n检查data_sources表中的数据:")
        cursor.execute("SELECT id, name, source_id FROM data_sources;")
        records = cursor.fetchall()
        for record in records:
            print(f"  ID: {record[0]}, Name: {record[1]}, Source ID: {record[2]}")
        
        conn.close()
                
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_columns()