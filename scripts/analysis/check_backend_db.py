import sqlite3
import os

def check_backend_db():
    db_path = "data/sport_lottery.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found")
        return
    
    try:
        # 连接到backend目录的数据库文件
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Backend数据库 - 比赛相关表统计 ===")
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
        
        print("\n=== Backend数据库 - 日志相关表统计 ===")
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
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking backend database: {e}")

if __name__ == "__main__":
    check_backend_db()