#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime

def insert_test_record():
    conn = sqlite3.connect('sport_lottery.db')
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