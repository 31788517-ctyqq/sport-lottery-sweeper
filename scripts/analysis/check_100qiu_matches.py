import sqlite3

# 连接数据库
conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()

# 查询100qiu比赛数据数量
cursor.execute("SELECT COUNT(*) FROM matches WHERE data_source = '100qiu'")
count = cursor.fetchone()[0]
print(f'100qiu比赛数据数量: {count}')

# 查询最近的几条记录
cursor.execute("SELECT match_identifier, home_team_id, away_team_id, league_id, status, external_id FROM matches WHERE data_source = '100qiu' ORDER BY created_at DESC LIMIT 5")
records = cursor.fetchall()
print('\n最近的5条100qiu比赛记录:')
for record in records:
    print(f'  {record}')

conn.close()