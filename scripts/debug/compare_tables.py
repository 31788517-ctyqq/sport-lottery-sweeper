import sqlite3

# 连接当前数据库
conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
current_tables = set([row[0] for row in cursor.fetchall()])
conn.close()

# 连接备份数据库
conn2 = sqlite3.connect('data/backups/sport_lottery.db.backup')
cursor2 = conn2.cursor()
cursor2.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
backup_tables = set([row[0] for row in cursor2.fetchall()])
conn2.close()

# 找出新增的表
new_tables = current_tables - backup_tables
removed_tables = backup_tables - current_tables

print(f'Current tables: {len(current_tables)}')
print(f'Backup tables: {len(backup_tables)}')
print(f'New tables added: {len(new_tables)}')
for table in sorted(new_tables):
    print(f'- {table}')

print(f'\nTables removed: {len(removed_tables)}')
for table in sorted(removed_tables):
    print(f'- {table}')