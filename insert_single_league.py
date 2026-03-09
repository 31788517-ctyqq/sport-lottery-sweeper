import sqlite3

conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()

try:
    cursor.execute("""
    INSERT INTO leagues (
        name, code, short_name, country, country_code, level, type, description,
        total_teams, total_matches, is_active, is_popular, is_national,
        total_views, total_followers, average_attendance, config
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('Premier League', 'EPL', 'PL', 'England', 'GB', 1, 'club', 'English Premier League', 20, 380, 1, 1, 1, 1000000, 500000, 40000, '{}'))
    
    conn.commit()
    print("League inserted successfully!")
    
except Exception as e:
    print(f"Error inserting league: {e}")

conn.close()