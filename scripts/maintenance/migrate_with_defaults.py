import sqlite3
from datetime import datetime

def migrate_with_defaults():
    conn = sqlite3.connect('data/sport_lottery.db')
    cursor = conn.cursor()
    
    # 联赛数据（提供所有必需字段的默认值）
    leagues_data = [
        ('Premier League', 'EPL', 'PL', 'England', 'GB', 1, 'club', 'English Premier League', 20, 380, 1, 1, 1, 1000000, 500000, 40000, '{}'),
        ('La Liga', 'ESP1', 'LL', 'Spain', 'ES', 1, 'club', 'Spanish La Liga', 20, 380, 1, 1, 1, 800000, 400000, 35000, '{}'),
        ('Bundesliga', 'GER1', 'BL', 'Germany', 'DE', 1, 'club', 'German Bundesliga', 18, 306, 1, 1, 1, 700000, 350000, 30000, '{}'),
        ('Serie A', 'ITA1', 'SA', 'Italy', 'IT', 1, 'club', 'Italian Serie A', 20, 380, 1, 1, 1, 600000, 300000, 25000, '{}'),
        ('Ligue 1', 'FRA1', 'L1', 'France', 'FR', 1, 'club', 'French Ligue 1', 18, 306, 1, 1, 1, 500000, 250000, 20000, '{}'),
        ('Champions League', 'UCL', 'UCL', 'Europe', 'EU', 1, 'cup', 'UEFA Champions League', 32, 125, 1, 1, 0, 900000, 450000, 50000, '{}'),
        ('Europa League', 'UEL', 'UEL', 'Europe', 'EU', 1, 'cup', 'UEFA Europa League', 48, 205, 1, 1, 0, 400000, 200000, 15000, '{}'),
        ('World Cup', 'WC', 'WC', 'World', 'INT', 1, 'cup', 'FIFA World Cup', 32, 64, 1, 1, 0, 2000000, 1000000, 60000, '{}'),
        ('European Championship', 'EC', 'EC', 'Europe', 'EU', 1, 'cup', 'UEFA European Championship', 24, 51, 1, 1, 0, 1500000, 750000, 55000, '{}'),
        ('Copa America', 'CA', 'CA', 'South America', 'INT', 1, 'cup', 'Copa America', 12, 26, 1, 1, 0, 300000, 150000, 18000, '{}'),
        ('Brasileirao', 'BRA1', 'BR', 'Brazil', 'BR', 1, 'club', 'Campeonato Brasileiro Serie A', 20, 380, 1, 1, 1, 200000, 100000, 12000, '{}'),
        ('Primera Division', 'ARG1', 'AR', 'Argentina', 'AR', 1, 'club', 'Argentine Primera Division', 28, 378, 1, 1, 1, 180000, 90000, 10000, '{}'),
        ('Primeira Liga', 'PLIG', 'PL', 'Portugal', 'PT', 1, 'club', 'Portuguese Primeira Liga', 18, 306, 1, 1, 1, 150000, 75000, 8000, '{}'),
        ('Eredivisie', 'EDE', 'ED', 'Netherlands', 'NL', 1, 'club', 'Dutch Eredivisie', 18, 306, 1, 1, 1, 120000, 60000, 7000, '{}'),
        ('Belgian Pro League', 'BPL', 'BPL', 'Belgium', 'BE', 1, 'club', 'Belgian Pro League', 18, 306, 1, 1, 1, 100000, 50000, 6000, '{}'),
        ('Austrian Bundesliga', 'AB', 'AB', 'Austria', 'AT', 1, 'club', 'Austrian Bundesliga', 12, 132, 1, 1, 1, 80000, 40000, 5000, '{}'),
        ('Swiss Super League', 'SSL', 'SSL', 'Switzerland', 'CH', 1, 'club', 'Swiss Super League', 12, 132, 1, 1, 1, 70000, 35000, 4500, '{}'),
        ('Scottish Premiership', 'SP', 'SP', 'Scotland', 'GB', 1, 'club', 'Scottish Premiership', 12, 132, 1, 1, 1, 60000, 30000, 4000, '{}'),
        ('Chinese Super League', 'CSL', 'CSL', 'China', 'CN', 1, 'club', 'Chinese Super League', 16, 240, 1, 1, 1, 500000, 250000, 20000, '{}'),
        ('J1 League', 'JPN1', 'J1', 'Japan', 'JP', 1, 'club', 'Japanese J1 League', 18, 306, 1, 1, 1, 300000, 150000, 15000, '{}')
    ]
    
    # 插入联赛数据
    for league in leagues_data:
        try:
            cursor.execute("""
            INSERT OR IGNORE INTO leagues (
                name, code, short_name, country, country_code, level, type, description,
                total_teams, total_matches, is_active, is_popular, is_national,
                total_views, total_followers, average_attendance, config
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, league)
        except Exception as e:
            print(f"Error inserting league {league[0]}: {e}")
    
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM leagues")
    leagues_count = cursor.fetchone()[0]
    print(f"Leagues migrated: {leagues_count}")
    
    # 球队数据
    teams_data = [
        ('Manchester United', 'Man United', 'MU', 'England', 'EPL', 1),
        ('Liverpool', 'Liverpool FC', 'LIV', 'England', 'EPL', 1),
        ('Manchester City', 'Man City', 'MC', 'England', 'EPL', 1),
        ('Chelsea', 'Chelsea FC', 'CFC', 'England', 'EPL', 1),
        ('Arsenal', 'Arsenal FC', 'ARS', 'England', 'EPL', 1),
        ('Tottenham Hotspur', 'Spurs', 'THFC', 'England', 'EPL', 1),
        ('Real Madrid', 'Real Madrid', 'RM', 'Spain', 'ESP1', 1),
        ('Barcelona', 'FC Barcelona', 'BAR', 'Spain', 'ESP1', 1),
        ('Atletico Madrid', 'Atletico', 'ATM', 'Spain', 'ESP1', 1),
        ('Sevilla', 'Sevilla FC', 'SEV', 'Spain', 'ESP1', 1),
        ('Valencia', 'Valencia CF', 'VAL', 'Spain', 'ESP1', 1),
        ('Real Sociedad', 'La Real', 'RSOC', 'Spain', 'ESP1', 1),
        ('Bayern Munich', 'Bayern', 'BAY', 'Germany', 'GER1', 1),
        ('Borussia Dortmund', 'BVB', 'BVB', 'Germany', 'GER1', 1),
        ('RB Leipzig', 'RBL', 'RBL', 'Germany', 'GER1', 1),
        ('Bayer Leverkusen', 'B04', 'B04', 'Germany', 'GER1', 1),
        ('Wolfsburg', 'WOB', 'WOB', 'Germany', 'GER1', 1),
        ('Eintracht Frankfurt', 'SGE', 'SGE', 'Germany', 'GER1', 1),
        ('Juventus', 'Juve', 'JUV', 'Italy', 'ITA1', 1),
        ('Inter Milan', 'Inter', 'INT', 'Italy', 'ITA1', 1),
        ('AC Milan', 'Milan', 'ACM', 'Italy', 'ITA1', 1),
        ('Napoli', 'Napoli', 'NAP', 'Italy', 'ITA1', 1),
        ('AS Roma', 'Roma', 'ROM', 'Italy', 'ITA1', 1),
        ('Lazio', 'Lazio', 'LAZ', 'Italy', 'ITA1', 1),
        ('Paris Saint-Germain', 'PSG', 'PSG', 'France', 'FRA1', 1),
        ('Olympique Marseille', 'OM', 'OM', 'France', 'FRA1', 1),
        ('Olympique Lyonnais', 'OL', 'OL', 'France', 'FRA1', 1),
        ('AS Monaco', 'ASM', 'ASM', 'France', 'FRA1', 1),
        ('LOSC Lille', 'LOSC', 'LOSC', 'France', 'FRA1', 1),
        ('Flamengo', 'Fla', 'FLA', 'Brazil', 'BRA1', 1),
        ('Palmeiras', 'PAL', 'PAL', 'Brazil', 'BRA1', 1),
        ('River Plate', 'Riv', 'RIV', 'Argentina', 'ARG1', 1),
        ('Boca Juniors', 'Boc', 'BOC', 'Argentina', 'ARG1', 1),
        ('Benfica', 'SLB', 'BEN', 'Portugal', 'PLIG', 1),
        ('Porto', 'FCP', 'POR', 'Portugal', 'PLIG', 1),
        ('Ajax', 'AFC', 'AJX', 'Netherlands', 'EDE', 1),
        ('PSV Eindhoven', 'PSV', 'PSV', 'Netherlands', 'EDE', 1),
        ('Club Brugge', 'CFCB', 'CLU', 'Belgium', 'BPL', 1),
        ('Red Bull Salzburg', 'RB Salzburg', 'RBS', 'Austria', 'AB', 1),
        ('Young Boys', 'YB', 'YB', 'Switzerland', 'SSL', 1),
        ('Celtic', 'CEL', 'CEL', 'Scotland', 'SP', 1),
        ('Rangers', 'RAN', 'RAN', 'Scotland', 'SP', 1),
        ('Guangzhou FC', 'GZFC', 'GZE', 'China', 'CSL', 1),
        ('Shanghai Port', 'SIPG', 'SHA', 'China', 'CSL', 1),
        ('Kawasaki Frontale', 'Kawasaki', 'KAW', 'Japan', 'JPN1', 1),
        ('Urawa Red Diamonds', 'Urawa', 'URD', 'Japan', 'JPN1', 1),
        ('Hilal', 'Al-Hilal', 'HIL', 'Saudi Arabia', 'SAUDI', 1),
        ('Nassr', 'Al-Nassr', 'NSR', 'Saudi Arabia', 'SAUDI', 1),
        ('Zamalek', 'Zamalek SC', 'ZSP', 'Egypt', 'EGYPT', 1),
        ('CSKA Moscow', 'CSKA', 'CSKA', 'Russia', 'RUSSIA', 1)
    ]
    
    # 插入球队数据
    for team in teams_data:
        try:
            cursor.execute("""
            INSERT OR IGNORE INTO teams (name, short_name, code, country, league_id, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
            """, team)
        except Exception as e:
            print(f"Error inserting team {team[0]}: {e}")
    
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM teams")
    teams_count = cursor.fetchone()[0]
    print(f"Teams migrated: {teams_count}")
    
    conn.close()
    print("Migration with defaults completed!")

if __name__ == "__main__":
    migrate_with_defaults()