import sqlite3

conn = sqlite3.connect('sport_lottery.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM ip_pools')
count = cursor.fetchone()[0]
print(f'IP pools records: {count}')

if count > 0:
    cursor.execute('SELECT ip, port, protocol, status FROM ip_pools LIMIT 5')
    rows = cursor.fetchall()
    print('Sample IPs:')
    for row in rows:
        print(f'- {row[0]}:{row[1]} ({row[2]}) [{row[3]}]')

conn.close()