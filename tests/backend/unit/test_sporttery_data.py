"""
测试从竞彩网获取比赛数据
"""
import asyncio
import json
from datetime import datetime, timedelta

from backend.app.scrapers.advanced_crawler import advanced_crawler


async def test_sporttery_crawler():
    print("开始测试从竞彩网获取比赛数据...")
    print("="*60)
    
    # 获取未来3天的比赛数据
    matches = await advanced_crawler.crawl_sporttery_matches(3)
    
    if not matches:
        print("未能获取到任何比赛数据")
        return
    
    print(f"共获取到 {len(matches)} 场比赛数据:\n")
    
    # 获取今天日期，用于分组显示
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)
    
    today_matches = []
    tomorrow_matches = []
    day_after_tomorrow_matches = []
    later_matches = []
    
    # 按日期分组
    for match in matches:
        match_time_str = match.get('match_time', '')
        try:
            if 'T' in match_time_str:
                match_date = datetime.fromisoformat(match_time_str.replace('Z', '+00:00')).date()
            elif ':' in match_time_str and '-' in match_time_str:
                if len(match_time_str.split()[0].split('-')[0]) == 4:
                    match_date = datetime.strptime(match_time_str.split()[0], "%Y-%m-%d").date()
                else:
                    # MM-DD格式
                    year = today.year
                    date_part = f"{year}-{match_time_str.split()[0]}"
                    match_date = datetime.strptime(date_part, "%Y-%m-%d").date()
            else:
                # 只有日期
                if '-' in match_time_str and len(match_time_str.split('-')[0]) == 4:
                    match_date = datetime.strptime(match_time_str, "%Y-%m-%d").date()
                else:
                    # 假设是MM-DD格式
                    year = today.year
                    match_date = datetime.strptime(f"{year}-{match_time_str}", "%Y-%m-%d").date()
            
            # 分组
            if match_date == today:
                today_matches.append(match)
            elif match_date == tomorrow:
                tomorrow_matches.append(match)
            elif match_date == day_after_tomorrow:
                day_after_tomorrow_matches.append(match)
            elif match_date > day_after_tomorrow:
                later_matches.append(match)
                
        except Exception as e:
            print(f"解析比赛时间失败: {match_time_str}, 错误: {str(e)}")
            # 如果解析失败，放入later_matches
            later_matches.append(match)
    
    # 显示今天比赛
    print(f"📅 今天 ({today.strftime('%Y-%m-%d')}) 的比赛: {len(today_matches)} 场")
    for idx, match in enumerate(today_matches, 1):
        print(f"  {idx}. [{match.get('league', 'N/A')}] {match.get('home_team', 'N/A')} VS {match.get('away_team', 'N/A')} - {match.get('match_time', 'N/A')}")
        print(f"     赔率: 主胜 {match.get('odds_home_win', 'N/A')} | 平局 {match.get('odds_draw', 'N/A')} | 客胜 {match.get('odds_away_win', 'N/A')}")
    
    # 显示明天比赛
    print(f"\n📅 明天 ({tomorrow.strftime('%Y-%m-%d')}) 的比赛: {len(tomorrow_matches)} 场")
    for idx, match in enumerate(tomorrow_matches, 1):
        print(f"  {idx}. [{match.get('league', 'N/A')}] {match.get('home_team', 'N/A')} VS {match.get('away_team', 'N/A')} - {match.get('match_time', 'N/A')}")
        print(f"     赔率: 主胜 {match.get('odds_home_win', 'N/A')} | 平局 {match.get('odds_draw', 'N/A')} | 客胜 {match.get('odds_away_win', 'N/A')}")
    
    # 显示后天比赛
    print(f"\n📅 后天 ({day_after_tomorrow.strftime('%Y-%m-%d')}) 的比赛: {len(day_after_tomorrow_matches)} 场")
    for idx, match in enumerate(day_after_tomorrow_matches, 1):
        print(f"  {idx}. [{match.get('league', 'N/A')}] {match.get('home_team', 'N/A')} VS {match.get('away_team', 'N/A')} - {match.get('match_time', 'N/A')}")
        print(f"     赔率: 主胜 {match.get('odds_home_win', 'N/A')} | 平局 {match.get('odds_draw', 'N/A')} | 客胜 {match.get('odds_away_win', 'N/A')}")
    
    # 显示后续比赛
    if later_matches:
        print(f"\n📅 后续比赛: {len(later_matches)} 场")
        for idx, match in enumerate(later_matches, 1):
            print(f"  {idx}. [{match.get('league', 'N/A')}] {match.get('home_team', 'N/A')} VS {match.get('away_team', 'N/A')} - {match.get('match_time', 'N/A')}")
            print(f"     赔率: 主胜 {match.get('odds_home_win', 'N/A')} | 平局 {match.get('odds_draw', 'N/A')} | 客胜 {match.get('odds_away_win', 'N/A')}")
    
    total_matches = len(today_matches) + len(tomorrow_matches) + len(day_after_tomorrow_matches)
    print(f"\n✅ 总计从今天开始的三天内共有 {total_matches} 场比赛")
    
    if total_matches == 0:
        print("\n⚠️  注意：未能获取到从今天开始的三天内的比赛数据，请检查爬虫配置或网站结构是否发生变化")


if __name__ == "__main__":
    asyncio.run(test_sporttery_crawler())