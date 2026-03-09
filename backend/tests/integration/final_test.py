"""
最终测试脚本 - 验证优化后的爬虫
"""
import asyncio
from .scrapers.advanced_crawler import advanced_crawler
from datetime import datetime


async def final_test():
    """
    最终测试验证爬虫功能
    """
    print("🏁 开始最终测试 - 验证优化后的爬虫功能")
    print("⚙️ 正在从竞彩网获取未来3天的比赛数据...")

    # 获取数据
    matches = await advanced_crawler.crawl_sporttery_matches(3)

    print(f'📊 获取到 {len(matches)} 条比赛数据')

    if matches:
        print("\n🎮 前5场比赛数据 ")
        for i, match in enumerate(matches[:5]):
            print(f"\n比赛 {i+1}:")
            print(f"  🏆 联赛: {match.get('league', 'N/A')}")
            print(f"  🆚 对阵: {match.get('home_team', 'N/A')} VS {match.get('away_team', 'N/A')}")
            print(f"  ⏰ 时间: {match.get('match_time', 'N/A')}")
            print(f"  📊 赔率: 主胜 {match.get('odds_home_win', 'N/A')}, 平局 {match.get('odds_draw', 'N/A')}, 客胜 {match.get('odds_away_win', 'N/A')}")
            print(f"  🔥 热门程度: {match.get('popularity', 'N/A')}")
            print(f"  📡 数据来源: {match.get('source', 'N/A')}")

    # 测试获取热门比赛
    print("\n🔥 获取热门比赛数据...")
    popular_matches = await advanced_crawler.get_popular_matches()
    print(f'📊 获取到 {len(popular_matches)} 场热门比赛')

    if popular_matches:
        print("\n🎮 热门比赛列表:")
        for i, match in enumerate(popular_matches[:3]):
            print(f"  {i+1}. {match.get('home_team', 'N/A')} VS {match.get('away_team', 'N/A')} - {match.get('league', 'N/A')}")

    # 测试获取趋势话题
    print("\n📈 获取趋势话题数据...")
    trending_topics = await advanced_crawler.get_trending_topics()
    print(f'📊 获取到 {len(trending_topics)} 个趋势话题')

    if trending_topics:
        print("\n🎮 趋势话题列表:")
        for i, topic in enumerate(trending_topics[:3]):
            print(f"  {i+1}. {topic.get('title', 'N/A')}")
            print(f"     来源: {topic.get('source', 'N/A')}, 热度: {topic.get('popularity', 'N/A')}")

    print(f"\n🎉 测试完成，总共获取到 {len(matches)} 场比赛数据)         ")

    # 按日期分组显示
    print("\n📅 按日期分组的比赛数据:")
    matches_by_date = {}
    for match in matches:
        match_time_str = match.get('match_time', '')
        if match_time_str:
            # 尝试解析时间字符串以获取日期部分
            try:
                if ':' in match_time_str and '-' in match_time_str:
                    if len(match_time_str.split()[0].split('-')[0]) == 4:
                        date_part = match_time_str.split()[0]  # YYYY-MM-DD
                    else:
                        # MM-DD HH:MM format
                        year = datetime.now().year
                        date_part = f"{year}-{match_time_str.split()[0]}"  # YYYY-MM-DD
                elif ':' in match_time_str:
                    # 只有时间，使用今天日期
                    date_part = datetime.now().strftime("%Y-%m-%d")
                else:
                    # 只有日期
                    if '-' in match_time_str and len(match_time_str.split('-')[0]) == 4:
                        date_part = match_time_str
                    else:
                        # MM-DD format
                        year = datetime.now().year
                        date_part = f"{year}-{match_time_str}"

                if date_part not in matches_by_date:
                    matches_by_date[date_part] = []
                matches_by_date[date_part].append(match)
            except:
                continue

    # 按日期排序并显示
    sorted_dates = sorted(matches_by_date.keys())

    for date in sorted_dates:
        date_matches = matches_by_date[date]
        print(f"\n📅 {date} 的比赛 {len(date_matches)} 场)")

        for idx, match in enumerate(date_matches, 1):
            league = match.get('league', 'N/A')
            home_team = match.get('home_team', 'N/A')
            away_team = match.get('away_team', 'N/A')
            time_part = match.get('match_time', 'N/A')
            print(f"  {idx}. [{league}] {home_team} VS {away_team} ({time_part})")


if __name__ == "__main__":
    asyncio.run(final_test())