import sqlite3

conn = sqlite3.connect('sport_lottery_current_20260209_235708.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f'Current database has {len(tables)} tables:')
for table in sorted(tables):
    print(f'- {table}')
conn.close()