#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_table_structure():
    conn = sqlite3.connect('sport_lottery.db')
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