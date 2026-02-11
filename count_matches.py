import sqlite3

def count_matches():
    try:
        # 连接到根目录的数据库文件
        conn = sqlite3.connect('sport_lottery.db')
        cursor = conn.cursor()
        
        # 检查所有可能包含比赛数据的表
        match_tables = ['football_matches', 'matches']
        
        for table in match_tables:
            try:
                # 获取表中的记录总数
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"Table '{table}': {count} matches")
                
                # 如果有数据，显示一些示例记录的结构
                if count > 0:
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    print(f"  Columns in {table}:")
                    for col in columns:
                        print(f"    - {col[1]} ({col[2]})")
                    
                    # 显示前2条记录作为示例
                    cursor.execute(f"SELECT * FROM {table} LIMIT 2")
                    sample_records = cursor.fetchall()
                    print(f"  Sample records (first 2):")
                    for record in sample_records:
                        print(f"    {record}")
                    print()
                    
            except sqlite3.OperationalError as e:
                print(f"Table '{table}' not found or error: {e}")
                print()
        
        conn.close()
        
    except Exception as e:
        print(f"Error counting matches: {e}")

if __name__ == "__main__":
    count_matches()