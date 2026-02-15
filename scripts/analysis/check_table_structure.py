import sqlite3

def check_table_structure():
    conn = sqlite3.connect('data/sport_lottery.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(llm_providers)')
    columns = cursor.fetchall()
    print('Columns:')
    for col in columns:
        print(f'  {col[1]}')
    conn.close()

if __name__ == '__main__':
    check_table_structure()

import sqlite3
import os

db_path = 'data/sport_lottery.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查admin_operation_logs表结构
    try:
        cursor.execute('PRAGMA table_info(admin_operation_logs)')
        columns = cursor.fetchall()
        print('AdminOperationLogs table structure:')
        for col in columns:
            nullable = "NOT NULL" if col[3] else "NULL"
            print(f'  {col[1]} ({col[2]}) - {nullable}')
    except sqlite3.OperationalError as e:
        print(f'AdminOperationLogs table error: {e}')
    
    print()
    
    # 检查admin_login_logs表结构
    try:
        cursor.execute('PRAGMA table_info(admin_login_logs)')
        columns = cursor.fetchall()
        print('AdminLoginLogs table structure:')
        for col in columns:
            nullable = "NOT NULL" if col[3] else "NULL"
            print(f'  {col[1]} ({col[2]}) - {nullable}')
    except sqlite3.OperationalError as e:
        print(f'AdminLoginLogs table error: {e}')
    
    print()
    
    # 检查crawler_task_logs表结构
    try:
        cursor.execute('PRAGMA table_info(crawler_task_logs)')
        columns = cursor.fetchall()
        print('CrawlerTaskLogs table structure:')
        for col in columns:
            nullable = "NOT NULL" if col[3] else "NULL"
            print(f'  {col[1]} ({col[2]}) - {nullable}')
    except sqlite3.OperationalError as e:
        print(f'CrawlerTaskLogs table error: {e}')
    
    conn.close()
else:
    print(f'Database does not exist at {db_path}')