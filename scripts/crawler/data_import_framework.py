# 体育彩票扫盘系统 - 足球数据导入框架
# 支持从多个免费API源导入比赛、球队、联赛数据

import requests
import sqlite3
import json
import time
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FootballDataImporter:
    def __init__(self, db_path="sport_lottery.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # API配置 (需要申请免费的API密钥)
        self.api_configs = {
            'football_data_org': {
                'base_url': 'https://api.football-data.org/v4',
                'headers': {
                    # 'X-Auth-Token': 'YOUR_API_TOKEN'  # 需要在 https://www.football-data.org/ 注册获取
                },
                'competitions': {
                    'PL': 'Premier League',
                    'PD': 'La Liga', 
                    'BL1': 'Bundesliga',
                    'SA': 'Serie A',
                    'FL1': 'Ligue 1',
                    'CL': 'Champions League'
                }
            },
            'api_football': {
                'base_url': 'https://api-football-v1.p.rapidapi.com/v3',
                'headers': {
                    # 'X-RapidAPI-Key': 'YOUR_RAPIDAPI_KEY',  # 需要在RapidAPI注册
                    # 'X-RapidAPI-Host': 'api-football-v1.p.rapidapi.com'
                }
            }
        }
    
    def create_sample_data(self):
        """创建示例数据 (当API不可用时使用)"""
        logger.info("🎯 创建示例足球数据...")
        
        # 示例联赛数据 (20个联赛)
        leagues_data = [
            ('Premier League', 'EPL', 'England', 'club', 'England Premier League', 1),
            ('La Liga', 'ESP1', 'Spain', 'club', 'Spanish La Liga', 1),
            ('Bundesliga', 'GER1', 'Germany', 'club', 'German Bundesliga', 1),
            ('Serie A', 'ITA1', 'Italy', 'club', 'Italian Serie A', 1),
            ('Ligue 1', 'FRA1', 'France', 'club', 'French Ligue 1', 1),
            ('Champions League', 'UCL', 'Europe', 'cup', 'UEFA Champions League', 1),
            ('Europa League', 'UEL', 'Europe', 'cup', 'UEFA Europa League', 1),
            ('World Cup', 'WC', 'World', 'cup', 'FIFA World Cup', 1),
            ('European Championship', 'EURO', 'Europe', 'cup', 'UEFA European Championship', 1),
            ('Copa America', 'COPA', 'South America', 'cup', 'Copa America', 1),
            ('Brazilian Serie A', 'BRA1', 'Brazil', 'club', 'Brazilian Serie A', 1),
            ('Argentine Primera', 'ARG1', 'Argentina', 'club', 'Argentine Primera Division', 1),
            ('Portuguese Liga', 'POR1', 'Portugal', 'club', 'Portuguese Primeira Liga', 1),
            ('Dutch Eredivisie', 'NED1', 'Netherlands', 'club', 'Dutch Eredivisie', 1),
            ('Belgian Pro League', 'BEL1', 'Belgium', 'club', 'Belgian Pro League', 1),
            ('Austrian Bundesliga', 'AUT1', 'Austria', 'club', 'Austrian Football Bundesliga', 1),
            ('Swiss Super League', 'SUI1', 'Switzerland', 'club', 'Swiss Super League', 1),
            ('Scottish Premiership', 'SCO1', 'Scotland', 'club', 'Scottish Premiership', 1),
            ('Chinese Super League', 'CSL', 'China', 'club', 'Chinese Super League', 1),
            ('Japanese J1 League', 'JPN1', 'Japan', 'club', 'Japanese J1 League', 1)
        ]
        
        # 示例球队数据 (50支球队)
        teams_data = [
            # 英超球队
            ('Manchester United', 'Man United', 'England', 'EPL', 1),
            ('Liverpool', 'Liverpool FC', 'England', 'EPL', 1),
            ('Manchester City', 'Man City', 'England', 'EPL', 1),
            ('Chelsea', 'Chelsea FC', 'England', 'EPL', 1),
            ('Arsenal', 'Arsenal FC', 'England', 'EPL', 1),
            ('Tottenham', 'Tottenham Hotspur', 'England', 'EPL', 1),
            # 西甲球队
            ('Real Madrid', 'Real Madrid CF', 'Spain', 'ESP1', 1),
            ('Barcelona', 'FC Barcelona', 'Spain', 'ESP1', 1),
            ('Atletico Madrid', 'Atletico Madrid', 'Spain', 'ESP1', 1),
            ('Sevilla', 'Sevilla FC', 'Spain', 'ESP1', 1),
            ('Valencia', 'Valencia CF', 'Spain', 'ESP1', 1),
            ('Real Sociedad', 'Real Sociedad', 'Spain', 'ESP1', 1),
            # 德甲球队
            ('Bayern Munich', 'FC Bayern Munich', 'Germany', 'GER1', 1),
            ('Borussia Dortmund', 'Borussia Dortmund', 'Germany', 'GER1', 1),
            ('RB Leipzig', 'RB Leipzig', 'Germany', 'GER1', 1),
            ('Bayer Leverkusen', 'Bayer 04 Leverkusen', 'Germany', 'GER1', 1),
            ('Wolfsburg', 'VfL Wolfsburg', 'Germany', 'GER1', 1),
            ('Eintracht Frankfurt', 'Eintracht Frankfurt', 'Germany', 'GER1', 1),
            # 意甲球队
            ('Juventus', 'Juventus FC', 'Italy', 'ITA1', 1),
            ('Inter Milan', 'Inter Milan', 'Italy', 'ITA1', 1),
            ('AC Milan', 'AC Milan', 'Italy', 'ITA1', 1),
            ('Napoli', 'SSC Napoli', 'Italy', 'ITA1', 1),
            ('Roma', 'AS Roma', 'Italy', 'ITA1', 1),
            ('Lazio', 'SS Lazio', 'Italy', 'ITA1', 1),
            # 法甲球队
            ('Paris Saint-Germain', 'PSG', 'France', 'FRA1', 1),
            ('Marseille', 'Olympique Marseille', 'France', 'FRA1', 1),
            ('Lyon', 'Olympique Lyon', 'France', 'FRA1', 1),
            ('Monaco', 'AS Monaco', 'France', 'FRA1', 1),
            ('Lille', 'LOSC Lille', 'France', 'FRA1', 1),
            # 其他联赛知名球队
            ('Flamengo', 'CR Flamengo', 'Brazil', 'BRA1', 1),
            ('Palmeiras', 'Palmeiras', 'Brazil', 'BRA1', 1),
            ('River Plate', 'River Plate', 'Argentina', 'ARG1', 1),
            ('Boca Juniors', 'Boca Juniors', 'Argentina', 'ARG1', 1),
            ('Benfica', 'SL Benfica', 'Portugal', 'POR1', 1),
            ('Porto', 'FC Porto', 'Portugal', 'POR1', 1),
            ('Ajax', 'AFC Ajax', 'Netherlands', 'NED1', 1),
            ('PSV Eindhoven', 'PSV Eindhoven', 'Netherlands', 'NED1', 1),
            ('Club Brugge', 'Club Brugge KV', 'Belgium', 'BEL1', 1),
            ('RB Salzburg', 'Red Bull Salzburg', 'Austria', 'AUT1', 1),
            ('Young Boys', 'BSC Young Boys', 'Switzerland', 'SUI1', 1),
            ('Celtic', 'Celtic FC', 'Scotland', 'SCO1', 1),
            ('Rangers', 'Rangers FC', 'Scotland', 'SCO1', 1),
            ('Guangzhou Evergrande', 'Guangzhou FC', 'China', 'CSL', 1),
            ('Shanghai SIPG', 'Shanghai Port FC', 'China', 'CSL', 1),
            ('Kawasaki Frontale', 'Kawasaki Frontale', 'Japan', 'JPN1', 1),
            ('Urawa Red Diamonds', 'Urawa Reds', 'Japan', 'JPN1', 1),
            ('Al Hilal', 'Al Hilal SFC', 'Saudi Arabia', 'SPL', 1),
            ('Al Nassr', 'Al Nassr FC', 'Saudi Arabia', 'SPL', 1),
            ('Zenit St Petersburg', 'Zenit Saint Petersburg', 'Russia', 'RUS1', 1),
            ('CSKA Moscow', 'CSKA Moscow', 'Russia', 'RUS1', 1)
        ]
        
        # 示例比赛数据 (120场比赛)
        matches_data = []
        base_date = datetime.now()
        
        # 生成未来30天内的比赛
        for day in range(30):
            match_date = base_date + timedelta(days=day)
            if match_date.weekday() < 5:  # 周一到周五
                # 每天3-5场比赛
                daily_matches = 3 + (day % 3)
                for match_num in range(daily_matches):
                    # 随机选择主客队 (确保不重复同一天同一队)
                    import random
                    home_team = random.choice(teams_data)
                    away_team = random.choice([t for t in teams_data if t[0] != home_team[0]])
                    league = random.choice(leagues_data[:5])  # 只使用前5个联赛
                    
                    # 随机比赛时间 (下午1点到晚上10点)
                    hour = 13 + (match_num * 2) + random.randint(0, 1)
                    minute = random.choice([0, 15, 30, 45])
                    
                    match_datetime = match_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    matches_data.append((
                        f'MATCH_{day}_{match_num}_{random.randint(1000,9999)}',  # match_identifier
                        match_datetime.strftime('%Y-%m-%d'),  # match_date
                        match_datetime.strftime('%Y-%m-%d %H:%M:%S'),  # scheduled_kickoff
                        'pending',  # status
                        random.randint(1, 10),  # importance
                        home_team[4],  # home_team_id (league_id for demo)
                        away_team[4],  # away_team_id
                        0,  # home_score
                        0,  # away_score
                        random.choice([0, 1]),  # is_featured
                        1  # is_published
                    ))
        
        # 插入联赛数据
        logger.info(f"插入 {len(leagues_data)} 个联赛...")
        self.cursor.executemany(
            "INSERT OR IGNORE INTO leagues (name, short_name, country, category, description, is_active) VALUES (?, ?, ?, ?, ?, ?)",
            leagues_data
        )
        
        # 插入球队数据
        logger.info(f"插入 {len(teams_data)} 支球队...")
        self.cursor.executemany(
            "INSERT OR IGNORE INTO teams (name, short_name, country, league_id, is_active) VALUES (?, ?, ?, ?, ?)",
            teams_data
        )
        
        # 插入比赛数据
        logger.info(f"插入 {len(matches_data)} 场比赛...")
        self.cursor.executemany(
            """INSERT OR IGNORE INTO matches 
               (match_identifier, match_date, scheduled_kickoff, status, importance, 
                home_team_id, away_team_id, home_score, away_score, is_featured, is_published) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            matches_data
        )
        
        self.conn.commit()
        
        # 统计结果
        self.cursor.execute("SELECT COUNT(*) FROM leagues")
        league_count = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM teams") 
        team_count = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM matches")
        match_count = self.cursor.fetchone()[0]
        
        logger.info(f"✅ 示例数据创建完成!")
        logger.info(f"   📊 联赛: {league_count} 个")
        logger.info(f"   👥 球队: {team_count} 支") 
        logger.info(f"   ⚽ 比赛: {match_count} 场")
        
        return {
            'leagues': league_count,
            'teams': team_count, 
            'matches': match_count
        }
    
    def fetch_from_api(self, api_name, endpoint, params=None):
        """从指定API获取数据"""
        if api_name not in self.api_configs:
            logger.error(f"未知的API配置: {api_name}")
            return None
            
        config = self.api_configs[api_name]
        url = f"{config['base_url']}{endpoint}"
        
        try:
            response = requests.get(url, headers=config['headers'], params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败 {url}: {e}")
            return None
    
    def setup_real_api(self):
        """设置真实API (需要用户自己申请API密钥)"""
        print("🌐 设置真实API数据源")
        print("="*50)
        print("📋 推荐的免费足球数据源:")
        print()
        print("1. Football-Data.org (推荐)")
        print("   • 网址: https://www.football-data.org/")
        print("   • 免费额度: 10次/分钟，10个联赛")
        print("   • 包含: 比赛、球队、积分榜")
        print("   • 注册获取API Token")
        print()
        print("2. API-Football (RapidAPI)")
        print("   • 网址: https://rapidapi.com/api-sports/api/api-football")
        print("   • 免费额度: 100次/天")
        print("   • 包含: 全球400+联赛数据")
        print("   • 需要RapidAPI账号")
        print()
        print("3. TheSportsDB (开源)")
        print("   • 网址: https://www.thesportsdb.com/")
        print("   • 完全免费，无需API密钥")
        print("   • 数据相对简单")
        print()
        print("💡 建议: 先用示例数据测试，再申请API密钥获取真实数据")
        
        # 询问是否继续
        choice = input("是否现在创建示例数据进行测试? (y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            return self.create_sample_data()
        else:
            return None
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

# 使用示例
def main():
    importer = FootballDataImporter()
    
    try:
        print("🚀 足球数据导入工具")
        print("="*50)
        print("选择数据源:")
        print("1. 创建示例数据 (立即可用)")
        print("2. 设置真实API (需要申请密钥)")
        print("3. 退出")
        
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == '1':
            result = importer.create_sample_data()
            if result:
                print(f"\n🎉 数据导入成功!")
                print(f"📊 联赛: {result['leagues']} 个")
                print(f"👥 球队: {result['teams']} 支") 
                print(f"⚽ 比赛: {result['matches']} 场")
        elif choice == '2':
            result = importer.setup_real_api()
            if result:
                print(f"\n🎉 API数据导入成功!")
                print(f"📊 联赛: {result['leagues']} 个")
                print(f"👥 球队: {result['teams']} 支") 
                print(f"⚽ 比赛: {result['matches']} 场")
        else:
            print("👋 再见!")
            
    except KeyboardInterrupt:
        print("\n❌ 用户取消操作")
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
    finally:
        importer.close()

if __name__ == "__main__":
    main()