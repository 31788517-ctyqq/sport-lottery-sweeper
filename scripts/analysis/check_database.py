"""
检查数据库中的表和数据
"""
import sqlite3
import os

def check_database():
    # 查找数据库文件
    db_path = 'backend/database.db'
    if not os.path.exists(db_path):
        # 尝试其他可能的路径
        import glob
        db_files = glob.glob('**/database.db', recursive=True)
        if db_files:
            db_path = db_files[0]
            print(f'使用数据库文件: {db_path}')
        else:
            print('未找到database.db文件')
            return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print('=== 数据库表列表 ===')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(table[0])

    print('\n=== data_sources 表数据 ===')
    try:
        cursor.execute('SELECT * FROM data_sources;')
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    except sqlite3.OperationalError as e:
        print(f'Error accessing data_sources table: {e}')

    print('\n=== crawler_configs 表数据 ===')
    try:
        cursor.execute('SELECT * FROM crawler_configs;')
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    except sqlite3.OperationalError as e:
        print(f'Error accessing crawler_configs table: {e}')

    print('\n=== sources 表数据 ===')
    try:
        cursor.execute('SELECT * FROM sources;')
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    except sqlite3.OperationalError as e:
        print(f'Error accessing sources table: {e}')

    conn.close()

if __name__ == "__main__":
    check_database()