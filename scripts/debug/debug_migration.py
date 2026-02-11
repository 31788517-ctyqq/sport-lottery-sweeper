import sqlite3
import re

# 读取示例数据
with open('data/seed/sport_lottery_sample_data.sql', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取第一个INSERT语句
insert_blocks = re.findall(r'(INSERT.*?;)', content, re.DOTALL | re.IGNORECASE)
first_insert = insert_blocks[0]

print("First INSERT statement:")
print(first_insert[:500])

# 连接数据库并尝试手动插入
conn = sqlite3.connect('sport_lottery.db')
cursor = conn.cursor()

# 手动插入一条联赛数据
try:
    cursor.execute("""
    INSERT OR IGNORE INTO leagues (name, code, short_name, country, type, description, is_active) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('Premier League', 'EPL', 'PL', 'England', 'club', 'English Premier League', 1))
    
    conn.commit()
    print("Manual insert successful!")
    
    cursor.execute("SELECT COUNT(*) FROM leagues")
    count = cursor.fetchone()[0]
    print(f"Leagues count after manual insert: {count}")
    
except Exception as e:
    print(f"Manual insert failed: {e}")

conn.close()