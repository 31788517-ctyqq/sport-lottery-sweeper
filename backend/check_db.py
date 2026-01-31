#!/usr/bin/env python3
"""
查看数据库表结构和内容
"""
import sqlite3
import logging
logger = logging.getLogger(__name__)
import os

db_path = "sport_lottery.db"

if not os.path.exists(db_path):
    logger.debug(f"数据库文件 {db_path} 不存在")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    logger.debug("=== 数据库表列表 ===")
    for table in tables:
        table_name = table[0]
        logger.debug(f"\n表名: {table_name}")
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        logger.debug("  字段结构:")
        for col in columns:
            logger.debug(f"    {col[1]} ({col[2]}) {'PRIMARY KEY' if col[5] else ''}")
        
        # 获取前3行数据预览
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
        rows = cursor.fetchall()
        if rows:
            logger.debug("  数据预览 (前3行):")
            for row in rows:
                logger.debug(f"    {row}")
        else:
            logger.debug("  无数据")
    
    conn.close()