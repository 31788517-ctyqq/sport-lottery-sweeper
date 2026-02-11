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

def check_table_structure():
    cursor = conn.cursor()
    
    # 查看matches表的SQL定义
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='matches'")
    result = cursor.fetchone()
    if result:
        print("Matches table SQL definition:")
        print(result[0])
    else:
        print("Table 'matches' not found")
    
    conn.close()

if __name__ == "__main__":
    check_table_structure()