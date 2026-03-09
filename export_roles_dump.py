#!/usr/bin/env python3
import sqlite3, json, os

db_path = os.path.join(os.getcwd(), 'data', 'sport_lottery.db')
print('using db:', db_path)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('SELECT id,name,level,is_system,status,permissions FROM roles')
rows = cursor.fetchall()

out = []
for r in rows:
    id,name,level,is_system,status,permissions = r
    try:
        perms = json.loads(permissions) if permissions else []
    except Exception:
        perms = permissions
    out.append({'id':id,'name':name,'level':level,'is_system':is_system,'status':status,'permissions':perms})

with open('roles_dump.json','w',encoding='utf-8') as f:
    json.dump(out,f,ensure_ascii=False,indent=2)

print('dumped', len(out), 'roles')
conn.close()
