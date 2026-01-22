#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('sport_lottery.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(crawler_configs);")
rows = cursor.fetchall()
print("crawler_configs 表结构:")
for row in rows:
    print(row)
conn.close()
