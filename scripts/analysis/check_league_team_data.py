import sqlite3

conn = sqlite3.connect('sport_lottery.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM leagues')
league_count = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM teams')
team_count = cursor.fetchone()[0]
print(f'联赛: {league_count}条, 球队: {team_count}条')

if team_count > 0:
    cursor.execute('SELECT league_id FROM teams LIMIT 5')
    league_ids = [row[0] for row in cursor.fetchall()]
    print(f'球队的league_id: {league_ids[:5]}')
    
    cursor.execute('SELECT id FROM leagues LIMIT 5')
    league_db_ids = [row[0] for row in cursor.fetchall()]
    print(f'联赛的id: {league_db_ids[:5]}')

conn.close()