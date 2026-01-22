import os
import sqlite3

project_root = r'c:\Users\11581\Downloads\sport-lottery-sweeper'
test_db_path = os.path.join(project_root, 'sport_lottery_test.db')

print(f'Database file exists: {os.path.exists(test_db_path)}')

if os.path.exists(test_db_path):
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    result = cursor.fetchone()
    print(f'Users table exists: {result}')
    conn.close()