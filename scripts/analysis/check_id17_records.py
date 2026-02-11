#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_id17_records():
    conn = sqlite3.connect('sport_lottery.db')
    cursor = conn.cursor()
    
    # 查询ID为17数据源可能的记录（match_id为001, 002, 003等）
    cursor.execute('SELECT match_id, home_team, away_team FROM football_matches WHERE match_id IN ("001", "002", "003") ORDER BY match_id')
    records = cursor.fetchall()
    print('Sample records for ID 17:')
    for record in records:
        print(f'  {record}')
    
    conn.close()

if __name__ == "__main__":
    check_id17_records()