import sqlite3

def check_log_table():
    """检查数据库中的日志表"""
    try:
        conn = sqlite3.connect('data/sport_lottery.db')
        cursor = conn.cursor()

        # 检查所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]

        print("数据库中存在的所有表:")
        for table in table_names:
            print(f"  - {table}")
        
        print()
        
        if 'log_entries' in table_names:
            print('✓ log_entries 表存在')
            cursor.execute('SELECT COUNT(*) FROM log_entries;')
            count = cursor.fetchone()[0]
            print(f'  log_entries 表中有 {count} 条记录')
            
            if count > 0:
                print('\n最近的5条日志记录:')
                cursor.execute('SELECT * FROM log_entries ORDER BY timestamp DESC LIMIT 5;')
                recent_logs = cursor.fetchall()
                for log in recent_logs:
                    print(f'  ID: {log[0]}, 时间: {log[1]}, 级别: {log[2]}, 模块: {log[3]}, 消息: {log[4][:50]}...')
        else:
            print('✗ log_entries 表不存在')
            
            # 检查相似的表名
            log_like_tables = [t for t in table_names if 'log' in t.lower()]
            if log_like_tables:
                print(f"\n但发现了类似的表名: {log_like_tables}")
                
        conn.close()
        print('\n数据库检查完成!')
        
    except Exception as e:
        print(f"数据库检查出错: {e}")

if __name__ == "__main__":
    check_log_table()