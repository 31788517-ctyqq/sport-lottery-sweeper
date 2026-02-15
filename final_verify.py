import sqlite3

conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()

tables = ['llm_providers', 'leagues', 'teams', 'users', 'crawler_tasks']
for table in tables:
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    count = cursor.fetchone()[0]
    print(f'{table}: {count} records')

conn.close()