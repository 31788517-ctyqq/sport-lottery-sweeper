import sqlite3

def check_db_structure():
    """检查数据库结构"""
    try:
        conn = sqlite3.connect('backend/sport_lottery.db')
        cursor = conn.cursor()

        # 获取所有表的详细信息
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        print('数据库表列表:')
        for i, table in enumerate(tables, 1):
            print(f'{i:2d}. {table[0]}')

        # 特别检查log_entries表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='log_entries';")
        result = cursor.fetchone()
        if result:
            print(f'\nlog_entries表存在，检查其结构:')
            cursor.execute('PRAGMA table_info(log_entries);')
            columns = cursor.fetchall()
            for col in columns:
                print(f'  {col[1]} ({col[2]}) {"PRIMARY KEY" if col[5] else ""} {"NOT NULL" if col[3] else "NULLABLE"}')
            
            # 检查表中的记录数
            cursor.execute('SELECT COUNT(*) FROM log_entries;')
            count = cursor.fetchone()[0]
            print(f'\nlog_entries 表中有 {count} 条记录')
        else:
            print('\nlog_entries表不存在')

        conn.close()
    except Exception as e:
        print(f"数据库检查出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_db_structure()