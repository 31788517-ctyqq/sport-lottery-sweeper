import sqlite3

conn = sqlite3.connect('backend/sport_lottery.db')
cursor = conn.cursor()

try:
    cursor.execute("PRAGMA table_info(admin_operation_logs)")
    columns = cursor.fetchall()
    print('admin_operation_logs表结构:')
    for col in columns:
        print(f"  {col[1]} ({col[2]}) - nullable: {col[3]}, default: {col[4]}, pk: {col[5]}")
        
    print('\n检查crawler_task_logs表是否存在:')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crawler_task_logs'")
    table = cursor.fetchone()
    if table:
        print(f"表 {table[0]} 存在")
        cursor.execute("PRAGMA table_info(crawler_task_logs)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - nullable: {col[3]}, default: {col[4]}, pk: {col[5]}")
    else:
        print("表 crawler_task_logs 不存在")
        
finally:
    conn.close()