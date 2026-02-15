import sqlite3

conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()

business_tables = ['matches', 'leagues', 'teams', 'sp_records', 'football_matches']
new_tables = ['crawler_tasks', 'ip_pools', 'llm_providers', 'request_headers']

for table in business_tables:
    cursor.execute(f'PRAGMA foreign_key_list({table})')
    fk_info = cursor.fetchall()
    references_new = [fk for fk in fk_info if fk[2] in new_tables]
    print(f'{table} references new tables: {len(references_new)}')
    for fk in references_new:
        print(f'  -> {fk[2]}.{fk[4]}')

conn.close()