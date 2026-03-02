#!/usr/bin/env python3
import sqlite3

path=r"c:\Users\11581\Documents\GitHub\sport-lottery-sweeper\data\sport_lottery.db"
conn=sqlite3.connect(path)
cursor=conn.cursor()
cursor.execute("SELECT id,name,level,is_system,status FROM roles ORDER BY id")
for row in cursor.fetchall():
    print(row)
conn.close()
