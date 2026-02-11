#!/usr/bin/env python3
"""
直接查询数据库中的所有数据源
"""

import sqlite3
from pathlib import Path

def direct_db_check():
    """直接查询数据库"""
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
        print("直接查询数据库中的所有数据源")
        print("=" * 60)
        
        # 查询所有数据源
        cursor.execute("SELECT id, name, source_id FROM data_sources ORDER BY id;")
        sources = cursor.fetchall()
        
        print(f"数据库中总共有 {len(sources)} 个数据源:")
        for source in sources:
            print(f"  ID: {source[0]}, Name: {source[1]}, Source ID: {source[2]}")
        
        # 特别关注ID为8的数据源
        cursor.execute("SELECT id, name, source_id, url FROM data_sources WHERE id = 8;")
        specific_source = cursor.fetchone()
        if specific_source:
            print(f"\n✅ 找到ID为8的数据源:")
            print(f"  ID: {specific_source[0]}")
            print(f"  Name: {specific_source[1]}")
            print(f"  Source ID: {specific_source[2]}")
            print(f"  URL: {specific_source[3]}")
        else:
            print(f"\n❌ 未找到ID为8的数据源")
        
        conn.close()
                
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    direct_db_check()