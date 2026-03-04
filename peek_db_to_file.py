#!/usr/bin/env python3
import sqlite3
path=r"c:\Users\11581\Documents\GitHub\sport-lottery-sweeper\data\sport_lottery.db"
conn=sqlite3.connect(path)
cursor=conn.cursor()
cursor.execute("SELECT id,name,level,is_system,status FROM roles ORDER BY id")
rows=cursor.fetchall()
with open('db_roles.txt','w',encoding='utf-8') as f:
    for row in rows:
        f.write(str(row)+'\n')
conn.close()
print('written')
