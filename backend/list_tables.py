#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def list_tables():
    conn = sqlite3.connect('sport_lottery.db')
    cursor = conn.cursor()
    
    # 查看所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Database tables:")
    for table in tables:
        print(f"  - {table[0]}")
    
    conn.close()

if __name__ == "__main__":
    list_tables()