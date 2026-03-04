#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_total_100qiu():
    conn = sqlite3.connect('data/sport_lottery.db')
    cursor = conn.cursor()
    
    # 查询所有以数字开头的match_id记录（100qiu数据）
    cursor.execute('SELECT COUNT(*) FROM football_matches WHERE match_id GLOB "[0-9]*"')
    count = cursor.fetchone()[0]
    print(f'Total 100qiu records: {count}')
    
    conn.close()

if __name__ == "__main__":
    check_total_100qiu()