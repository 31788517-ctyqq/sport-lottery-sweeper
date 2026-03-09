#!/usr/bin/env python3
"""
获取数据库表信息
"""

import sqlite3
from pathlib import Path

def get_db_tables():
    """获取数据库表信息"""
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
        
        print("=" * 60)
        print("数据库表及行数")
        print("=" * 60)
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            if not table_name.startswith('sqlite_'):
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        print(f"{table_name}: {count} 行")
                except Exception as e:
                    print(f"{table_name}: 无法查询 ({e})")
        
        conn.close()
                
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    get_db_tables()