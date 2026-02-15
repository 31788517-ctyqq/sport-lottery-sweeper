import sqlite3

conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()

# 测试100球比赛查询
cursor.execute('SELECT COUNT(*) FROM matches WHERE match_identifier LIKE "MATCH_%"')
match_count = cursor.fetchone()[0]
print(f'100球比赛数据: {match_count}条')

# 测试联赛球队关联
cursor.execute('SELECT COUNT(*) FROM teams t JOIN leagues l ON t.league_id = l.id')
team_league_count = cursor.fetchone()[0]
print(f'联赛-球队关联数据: {team_league_count}条')

# 测试竞彩记录
cursor.execute('SELECT COUNT(*) FROM sp_records')
sp_count = cursor.fetchone()[0]
print(f'竞彩记录: {sp_count}条')

conn.close()