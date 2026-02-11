import sqlite3

conn = sqlite3.connect('sport_lottery.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(llm_providers)')
columns = cursor.fetchall()
print('LLM Providers columns:')
for col in columns:
    print(f'- {col[1]} ({col[2]})')
conn.close()