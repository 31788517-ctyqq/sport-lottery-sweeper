import sqlite3

conn = sqlite3.connect('sport_lottery.db')
cursor = conn.cursor()

tables = ['crawler_configs', 'crawler_tasks', 'data_sources']
for table in tables:
    try:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f'{table}: {count} records')
    except Exception as e:
        print(f'{table}: table not exists or error - {e}')

conn.close()