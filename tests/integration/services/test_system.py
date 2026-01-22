"""
测试优化后的爬虫系统
"""
import asyncio
import pytest
from backend.scrapers.advanced_crawler import advanced_crawler


@pytest.mark.asyncio
async def test_system():
    print("🔧 测试优化后的爬虫系统...")
    
    # 获取比赛数据
    matches = await advanced_crawler.crawl_sporttery_matches(3)
    
    print(f'✅ 获取到 {len(matches)} 场比赛数据')
    
    if matches:
        print("\n📊 前3场比赛预览:")
        for i, match in enumerate(matches[:3]):
            print(f"  {i+1}. {match.get('home_team', 'N/A')} VS {match.get('away_team', 'N/A')} "
                  f"[{match.get('league', 'N/A')}]")
    
    # 测试获取热门比赛
    popular_matches = await advanced_crawler.get_popular_matches()
    print(f'🔥 获取到 {len(popular_matches)} 场热门比赛')
    
    # 测试获取趋势话题
    trending_topics = await advanced_crawler.get_trending_topics()
    print(f'📈 获取到 {len(trending_topics)} 个趋势话题')
    
    print("\n🎉 系统测试完成!")


if __name__ == "__main__":
    asyncio.run(test_system())