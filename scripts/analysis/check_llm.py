import sqlite3

conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
llm_tables = [table for table in tables if 'llm' in table.lower()]
print(f'LLM related tables: {llm_tables}')

# 检查关键业务表
key_tables = ['users', 'roles', 'data_sources', 'crawler_tasks']
missing_tables = []
for table in key_tables:
    if table not in tables:
        missing_tables.append(table)

print(f'Missing key tables: {missing_tables}')
conn.close()