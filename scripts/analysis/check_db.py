import sqlite3

# Connect to database
conn = sqlite3.connect('test.db')
cursor = conn.cursor()

# Check admin_login_logs table
try:
    cursor.execute('SELECT COUNT(*) FROM admin_login_logs')
    count = cursor.fetchone()[0]
    print(f'Admin login logs count: {count}')
    
    if count > 0:
        cursor.execute('SELECT * FROM admin_login_logs LIMIT 1')
        row = cursor.fetchone()
        print(f'Sample row: {row}')
    else:
        print('No admin login logs found')
        
except sqlite3.OperationalError as e:
    print(f'Table not found: {e}')

# Check log_entries table
try:
    cursor.execute('SELECT COUNT(*) FROM log_entries WHERE module = "security"')
    security_count = cursor.fetchone()[0]
    print(f'Security logs in log_entries: {security_count}')
except sqlite3.OperationalError as e:
    print(f'Log entries table issue: {e}')

conn.close()