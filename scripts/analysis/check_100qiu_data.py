#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_100qiu_data():
    conn = sqlite3.connect('data/sport_lottery.db')
    cursor = conn.cursor()
    
    # 查询match_id以数字开头的记录（100qiu的数据）
    cursor.execute('SELECT match_id, home_team, away_team, league FROM football_matches WHERE match_id GLOB "[0-9]*" ORDER BY match_id LIMIT 5')
    records = cursor.fetchall()
    print('Sample 100qiu records:')
    for record in records:
        print(f'  {record}')
    
    # 查询总数
    cursor.execute('SELECT COUNT(*) FROM football_matches WHERE match_id GLOB "[0-9]*"')
    count = cursor.fetchone()[0]
    print(f'Total 100qiu records: {count}')
    
    conn.close()

if __name__ == "__main__":
    check_100qiu_data()