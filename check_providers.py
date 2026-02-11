import sqlite3
conn = sqlite3.connect('sport_lottery.db')
cur = conn.cursor()
cur.execute('SELECT name, provider_type FROM llm_providers')
rows = cur.fetchall()
print('All providers:')
for row in rows:
    print(f'  {row[0]}: {row[1]}')
conn.close()
