#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_new_id17_records():
    conn = sqlite3.connect('data/sport_lottery.db')
    cursor = conn.cursor()
    
    # 查询2026-01-13和2026-01-14日期的新记录
    cursor.execute('SELECT match_id, home_team, away_team FROM football_matches WHERE match_id LIKE "2026-01-13_%" OR match_id LIKE "2026-01-14_%" ORDER BY match_id LIMIT 5')
    records = cursor.fetchall()
    print('New records for ID 17:')
    for record in records:
        print(f'  {record}')
    
    # 查询总数
    cursor.execute('SELECT COUNT(*) FROM football_matches WHERE match_id LIKE "2026-01-13_%" OR match_id LIKE "2026-01-14_%"')
    count = cursor.fetchone()[0]
    print(f'Total new records for ID 17: {count}')
    
    conn.close()

if __name__ == "__main__":
    check_new_id17_records()