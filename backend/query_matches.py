#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# 导入数据库工具
try:
    from backend.database_utils import get_db_connection
    conn = get_db_connection()
except ImportError:
    # 回退方案
    import sqlite3
    conn = sqlite3.connect('data/sport_lottery.db')

def query_matches():
    cursor = conn.cursor()
    
    # 查看表结构
    cursor.execute("PRAGMA table_info(matches)")
    columns = cursor.fetchall()
    print("Matches table columns:")
    for col in columns:
        print(f"  {col}")
    
    # 查询总比赛数
    cursor.execute("SELECT COUNT(*) FROM matches")
    total = cursor.fetchone()[0]
    print(f"\nTotal matches: {total}")
    
    # 查询最新的5条记录（只查询存在的列）
    if total > 0:
        cursor.execute("SELECT id FROM matches ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        print("Latest 5 match IDs:")
        for row in rows:
            print(f"ID: {row[0]}")
    
    conn.close()

if __name__ == "__main__":
    query_matches()