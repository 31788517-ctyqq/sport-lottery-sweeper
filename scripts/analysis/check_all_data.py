import sqlite3

def check_all_data():
    try:
        # 连接到根目录的数据库文件
        conn = sqlite3.connect('data/sport_lottery.db')
        cursor = conn.cursor()
        
        # 检查所有可能包含比赛数据的表
        print("=== 比赛相关表统计 ===")
        match_tables = [
            'football_matches', 
            'matches', 
            'caipiao_data',
            'sp_records'
        ]
        
        for table in match_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"Table '{table}': {count} records")
            except sqlite3.OperationalError as e:
                print(f"Table '{table}' not found or error: {e}")
        
        print("\n=== 日志相关表统计 ===")
        log_tables = [
            'log_entries',
            'admin_operation_logs', 
            'admin_login_logs',
            'crawler_task_logs',
            'user_activities'
        ]
        
        total_logs = 0
        for table in log_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"Table '{table}': {count} records")
                total_logs += count
            except sqlite3.OperationalError as e:
                print(f"Table '{table}' not found or error: {e}")
        
        print(f"\nTotal log records: {total_logs}")
        
        # 检查是否有其他可能的比赛表
        print("\n=== 其他可能相关的表 ===")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%match%' OR name LIKE '%game%' OR name LIKE '%fixture%')")
        other_match_tables = cursor.fetchall()
        for table in other_match_tables:
            if table[0] not in match_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    print(f"Table '{table[0]}': {count} records")
                except sqlite3.OperationalError as e:
                    print(f"Table '{table[0]}' error: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking data: {e}")

if __name__ == "__main__":
    check_all_data()