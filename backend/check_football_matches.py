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

def check_football_matches():
    cursor = conn.cursor()
    
    # 查看football_matches表结构
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='football_matches'")
    result = cursor.fetchone()
    if result:
        print("football_matches table structure:")
        print(result[0])
    else:
        print("Table 'football_matches' not found")
    
    # 查看表中的数据
    cursor.execute("SELECT COUNT(*) FROM football_matches")
    count = cursor.fetchone()[0]
    print(f"\nTotal football_matches records: {count}")
    
    if count > 0:
        cursor.execute("SELECT id, match_id, home_team, away_team, match_time FROM football_matches ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        print("\nLatest 5 football_matches records:")
        for row in rows:
            print(f"  ID: {row[0]}, match_id: {row[1]}, {row[2]} vs {row[3]}, time: {row[4]}")
    
    conn.close()

if __name__ == "__main__":
    check_football_matches()