import sqlite3

conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f'Total tables after merge: {len(tables)}')

# 检查关键表
key_tables = ['llm_providers', 'ip_pools', 'request_headers', 'crawler_tasks', 'leagues', 'teams', 'users', 'roles']
missing = []
for table in key_tables:
    if table not in tables:
        missing.append(table)

print(f'Missing key tables: {missing}')
print(f'All key tables present: {len(missing) == 0}')

conn.close()