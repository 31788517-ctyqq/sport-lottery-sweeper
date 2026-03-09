import sqlite3

backup_conn = sqlite3.connect('data/backups/sport_lottery.db.backup')
backup_cursor = backup_conn.cursor()

# 检查传统业务表
traditional_tables = ['leagues', 'teams', 'matches', 'football_matches', 'odds_companies', 'sp_records']

print("Checking traditional business tables:")
for table in traditional_tables:
    try:
        backup_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = backup_cursor.fetchone()[0]
        print(f"- {table}: {count} records")
        
        if count > 0:
            # 查看前几条记录的结构
            backup_cursor.execute(f"SELECT * FROM {table} LIMIT 1")
            columns = [description[0] for description in backup_cursor.description]
            print(f"  Columns: {columns}")
            
    except Exception as e:
        print(f"- {table}: NOT EXISTS or ERROR - {e}")

backup_conn.close()