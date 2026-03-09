import sqlite3

try:
    conn = sqlite3.connect('data/samples/sport_lottery.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ip_pools'")
    exists = cursor.fetchone()
    
    if exists:
        cursor.execute('SELECT COUNT(*) FROM ip_pools')
        count = cursor.fetchone()[0]
        print(f'Sample DB IP pools: {count} records')
    else:
        print('Sample DB: ip_pools table not exists')
    
    conn.close()
except Exception as e:
    print(f'Error: {e}')