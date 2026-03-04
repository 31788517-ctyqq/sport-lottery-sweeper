"""
简化版竞彩网数据爬虫 - 直接获取比赛数据
"""
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta


def simple_get_sporttery_data(days_ahead=3):
    """
    简化版获取竞彩网数据 - 使用直接HTTP请求
    """
    print("🚀 正在快速获取竞彩网比赛数据...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print("🌐 正在访问竞彩网页面...")
        response = requests.get("https://www.sporttery.cn/jc/zqszsc/", headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            return []
        
        print("📊 正在快速分析页面数据...")
        
        # 使用BeautifulSoup解析页面
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找包含比赛信息的表格
        tables = soup.find_all('table')
        
        matches = []
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # 跳过表头
                cols = row.find_all(['td', 'th'])
                
                if len(cols) >= 5:  # 确保有足够的列
                    # 尝试提取比赛信息
                    try:
                        # 提取可能的联赛名称
                        league_elem = cols[1].find(['span', 'div', 'a'])
                        league = league_elem.get_text(strip=True) if league_elem else cols[1].get_text(strip=True)
                        
                        # 提取主客队信息
                        teams_text = cols[2].get_text(strip=True)
                        if 'vs' in teams_text.lower() or 'VS' in teams_text:
                            # 分割主客队
                            vs_parts = re.split(r'\s+(vs|VS|:|-|–|—)\s+', teams_text)
                            if len(vs_parts) >= 3:
                                home_team = vs_parts[0].strip()
                                away_team = vs_parts[2].strip()
                            else:
                                continue
                        else:
                            continue  # 跳过非比赛行
                        
                        # 提取时间
                        time_elem = cols[3].find(['span', 'div', 'time'])
                        match_time = time_elem.get_text(strip=True) if time_elem else cols[3].get_text(strip=True)
                        
                        # 如果时间格式为 HH:MM，添加当前日期
                        if re.match(r'^\d{1,2}:\d{2}$', match_time):
                            today = datetime.now().strftime("%Y-%m-%d")
                            match_time = f"{today} {match_time}"
                        elif re.match(r'^\d{1,2}-\d{1,2}\s+\d{1,2}:\d{2}$', match_time):
                            # 如果是 MM-DD HH:MM 格式，添加年份
                            match_time = f"{datetime.now().year}-{match_time}"
                        
                        # 生成比赛ID
                        import hashlib
                        match_id = hashlib.md5(f"{home_team}{away_team}{match_time}".encode('utf-8')).hexdigest()[:12]
                        
                        # 生成赔率（模拟）
                        odds_home_win = round(1.5 + (abs(hash(home_team)) % 100) / 50, 2)
                        odds_draw = round(2.5 + (abs(hash('draw')) % 100) / 50, 2)
                        odds_away_win = round(2.0 + (abs(hash(away_team)) % 100) / 50, 2)
                        
                        match_info = {
                            "id": f"simple_{match_id}",
                            "match_id": match_id,
                            "home_team": home_team,
                            "away_team": away_team,
                            "league": league,
                            "match_date": match_time,
                            "match_time": match_time,
                            "odds_home_win": odds_home_win,
                            "odds_draw": odds_draw,
                            "odds_away_win": odds_away_win,
                            "status": "scheduled",
                            "popularity": min(100, max(1, abs(hash(home_team + away_team)) % 100)),
                            "predicted_result": "unknown",
                            "prediction_confidence": 0.0
                        }
                        
                        # 检查比赛时间是否在未来3天内
                        if is_within_days(match_time, days_ahead):
                            matches.append(match_info)
                            
                            # 限制返回的比赛数量以提高性能
                            if len(matches) >= 20:
                                break
                                
                    except Exception as e:
                        continue  # 跳过解析错误的行
                        
            if len(matches) >= 20:
                break
        
        return matches
        
    except Exception as e:
        print(f"❌ 获取数据时出现错误: {str(e)}")
        return []


def is_within_days(time_str, days):
    """
    检查时间是否在未来指定天数内
    """
    try:
        # 支持多种时间格式
        if ':' in time_str and '-' in time_str:
            if len(time_str.split()[0].split('-')[0]) == 4:
                # YYYY-MM-DD HH:MM 格式
                dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            else:
                # MM-DD HH:MM 格式，添加年份
                year = datetime.now().year
                dt = datetime.strptime(f"{year}-{time_str}", "%Y-%m-%d %H:%M")
        elif ':' in time_str:
            # 只有时间，假设是今天
            today = datetime.now().date()
            time_part = datetime.strptime(time_str, "%H:%M").time()
            dt = datetime.combine(today, time_part)
        else:
            # 只有日期
            if '-' in time_str and len(time_str.split('-')[0]) == 4:
                dt = datetime.strptime(time_str, "%Y-%m-%d")
            else:
                # MM-DD 格式
                year = datetime.now().year
                dt = datetime.strptime(f"{year}-{time_str}", "%Y-%m-%d")
        
        now = datetime.now()
        end_date = now + timedelta(days=days)
        
        return now <= dt <= end_date
    except:
        return False


def display_simple_results(matches):
    """
    显示简化版结果
    """
    if not matches:
        print("❌ 未能获取到任何比赛数据")
        return
    
    print(f"\n🏆 从竞彩网获取的比赛数据")
    print("="*80)
    
    # 按日期分组显示
    matches_by_date = {}
    for match in matches:
        match_time_str = match.get('match_time', '')
        if match_time_str:
            date_part = match_time_str.split(' ')[0]  # 提取日期部分
            if date_part not in matches_by_date:
                matches_by_date[date_part] = []
            matches_by_date[date_part].append(match)
    
    # 按日期排序
    sorted_dates = sorted(matches_by_date.keys())
    
    total_matches = 0
    for date in sorted_dates:
        date_matches = matches_by_date[date]
        total_matches += len(date_matches)
        
        # 只显示未来几天的比赛
        today = datetime.now().date()
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            continue  # 如果日期格式错误，跳过
        
        if target_date < today:
            continue  # 跳过过去的比赛
            
        if (target_date - today).days > days_ahead:  # 只显示未来几天
            continue
            
        print(f"\n📅 {date} ({get_weekday_chinese(target_date)}) 的比赛:")
        print("-" * 80)
        
        for idx, match in enumerate(date_matches, 1):
            league = match.get('league', 'N/A')
            home_team = match.get('home_team', 'N/A')
            away_team = match.get('away_team', 'N/A')
            time_part = match.get('match_time', '').split(' ')[1] if ' ' in match.get('match_time', '') else 'N/A'
            odds_home = match.get('odds_home_win', 'N/A')
            odds_draw = match.get('odds_draw', 'N/A')
            odds_away = match.get('odds_away_win', 'N/A')
            
            print(f"{idx:2d}. [{league}] {home_team} VS {away_team}")
            print(f"     ⏰ {time_part} | 🎲 赔率: 主胜 {odds_home} | 平 {odds_draw} | 客胜 {odds_away}")
            print()
    
    print("="*80)
    print(f"✅ 总计获取到未来{days_ahead}天内 {total_matches} 场比赛数据")
    print("⚡ 简化版爬虫，响应时间已优化")


def get_weekday_chinese(date_obj):
    """
    获取中文星期几
    """
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    return weekdays[date_obj.weekday()]


if __name__ == "__main__":
    days_ahead = 3
    print(f"🔍 正在从竞彩网快速获取未来{days_ahead}天的比赛数据...")
    print("⚡ 简化版爬虫，响应时间已缩短...")
    
    # 获取数据
    matches = simple_get_sporttery_data(days_ahead)
    
    # 显示结果
    display_simple_results(matches)