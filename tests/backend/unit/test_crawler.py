"""
测试爬虫功能
"""
from backend.app.scrapers.advanced_crawler import advanced_crawler
import asyncio

async def test_crawler():
    print("开始测试爬虫功能...")
    result = await advanced_crawler.crawl_sporttery_matches(1)
    print(f'获取到 {len(result)} 条比赛数据')
    
    for i, match in enumerate(result[:3]):  # 只显示前3条
        print(f"{i+1}. {match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')} - {match.get('league', 'N/A')}")
    
    if not result:
        print("没有获取到任何比赛数据")

if __name__ == "__main__":
    asyncio.run(test_crawler())