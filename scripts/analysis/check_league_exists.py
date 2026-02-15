import sqlite3

conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM leagues WHERE code = ?', ('EPL',))
result = cursor.fetchone()
print('EPL league exists:', result is not None)

if result:
    print('Existing EPL record:', result)

conn.close()