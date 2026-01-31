import sqlite3

conn = sqlite3.connect('backend/sport_lottery.db')
cursor = conn.cursor()

try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print('数据库中的所有表:')
    for table in tables:
        print(table[0])
        
    print('\n检查日志相关表的数据量:')
    log_tables = ['log_entries', 'admin_login_logs', 'admin_operation_logs', 'sp_modification_logs']
    for table in log_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count} 条记录")
        except sqlite3.OperationalError as e:
            print(f"{table}: 表不存在 ({e})")
    
finally:
    conn.close()