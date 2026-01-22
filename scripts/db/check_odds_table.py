import sqlite3

conn = sqlite3.connect('sport_lottery.db')
cursor = conn.cursor()
cursor.execute('SELECT sql FROM sqlite_master WHERE name="odds"')
result = cursor.fetchone()
if result:
    print("odds表的SQL定义:")
    print(result[0])
else:
    print("odds表不存在")
conn.close()