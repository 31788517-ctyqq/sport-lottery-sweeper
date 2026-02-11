import sqlite3

conn = sqlite3.connect('sport_lottery.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM user_activities')
count = cursor.fetchone()[0]
print(f'User activities: {count} records')

if count > 0:
    cursor.execute('SELECT * FROM user_activities LIMIT 3')
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    for row in rows:
        record = dict(zip(columns, row))
        print(record)

conn.close()