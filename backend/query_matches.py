#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def query_matches():
    conn = sqlite3.connect('sport_lottery.db')
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