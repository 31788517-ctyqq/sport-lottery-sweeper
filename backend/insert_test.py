#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path
import sqlite3
from datetime import datetime

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

def insert_test_record():
    cursor = conn.cursor()
    
    # 插入测试记录
    cursor.execute(
        "INSERT INTO football_matches (match_id, home_team, away_team, match_time, league, status) VALUES (?, ?, ?, ?, ?, ?)",
        ('001', '测试主队', '测试客队', '2026-02-07 20:00:00', '测试联赛', 'pending')
    )
    conn.commit()
    conn.close()
    print("Test record inserted successfully")

if __name__ == "__main__":
    insert_test_record()