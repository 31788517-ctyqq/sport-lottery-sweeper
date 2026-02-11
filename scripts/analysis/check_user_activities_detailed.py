import sqlite3

conn = sqlite3.connect('sport_lottery.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(user_activities)')
columns = cursor.fetchall()
for col in columns:
    print(f'{col[1]}: {col[2]} (nullable: {not bool(col[3])})')
conn.close()