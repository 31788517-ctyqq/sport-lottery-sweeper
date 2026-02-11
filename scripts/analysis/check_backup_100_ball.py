import sqlite3

# 检查备份数据库
backup_conn = sqlite3.connect('data/backups/sport_lottery.db.backup')
backup_cursor = backup_conn.cursor()

# 查找包含100或ball的表
backup_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%100%' OR name LIKE '%ball%')")
backup_tables = backup_cursor.fetchall()
print('Backup tables containing "100" or "ball":')
for table in backup_tables:
    print(f'- {table[0]}')
    
    # 检查数据量
    backup_cursor.execute(f'SELECT COUNT(*) FROM {table[0]}')
    count = backup_cursor.fetchone()[0]
    print(f'  Records: {count}')

backup_conn.close()