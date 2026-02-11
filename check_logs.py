import sqlite3
conn = sqlite3.connect('sport_lottery.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM log_entries;')
count = cursor.fetchone()[0]
print('log_entries table has %d records' % count)
cursor.execute('SELECT * FROM log_entries ORDER BY timestamp DESC LIMIT 5;')
rows = cursor.fetchall()
print('Last 5 log records:')
for row in rows:
    print(row)
conn.close()
