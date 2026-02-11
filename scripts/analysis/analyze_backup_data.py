import sqlite3

# 连接备份数据库
backup_conn = sqlite3.connect('data/backups/sport_lottery.db.backup')
backup_cursor = backup_conn.cursor()

# 获取所有表名
backup_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
backup_tables = [row[0] for row in backup_cursor.fetchall()]

print("Backup database table counts:")
for table in sorted(backup_tables):
    try:
        backup_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = backup_cursor.fetchone()[0]
        if count > 0:
            print(f"- {table}: {count} records")
    except Exception as e:
        print(f"- {table}: ERROR - {e}")

backup_conn.close()