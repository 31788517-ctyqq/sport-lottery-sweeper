import sqlite3

conn = sqlite3.connect('data/backups/sport_lottery.db.backup')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f'Backup has {len(tables)} tables:')
for table in sorted(tables):
    print(f'- {table}')
conn.close()