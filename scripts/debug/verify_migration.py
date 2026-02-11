import sqlite3

conn = sqlite3.connect('sport_lottery.db')
cursor = conn.cursor()

# 验证传统业务表数据
traditional_tables = ['leagues', 'teams', 'matches']
for table in traditional_tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{table}: {count} records")

# 验证AI功能表数据
ai_tables = ['llm_providers']
for table in ai_tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{table}: {count} records")

conn.close()