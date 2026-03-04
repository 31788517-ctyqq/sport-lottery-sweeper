import sqlite3

conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_activities'")
result = cursor.fetchone()
print(f'User activities table exists: {result is not None}')
conn.close()