import sqlite3

conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()

tables = ['crawler_tasks', 'ip_pools', 'llm_providers', 'request_headers']
for table in tables:
    cursor.execute(f'PRAGMA foreign_key_list({table})')
    fk_info = cursor.fetchall()
    print(f'{table} foreign keys: {len(fk_info)}')
    for fk in fk_info:
        print(f'  -> references {fk[2]}.{fk[4]}')

conn.close()