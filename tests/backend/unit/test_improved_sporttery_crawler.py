"""
测试改进后的爬虫功能
"""
import asyncio
from backend.app.scrapers.advanced_crawler import advanced_crawler
from backend.app.scrapers.sporttery_scraper import sporttery_scraper


async def test_improved_sporttery_crawler():
    print("开始测试改进后的竞彩网爬虫...")
    
    # 测试使用advanced_crawler
    print("\n=== 测试 advanced_crawler ===")
    try:
        matches = await advanced_crawler.crawl_sporttery_matches(3)
        print(f"通过 advanced_crawler 获取到 {len(matches)} 条比赛数据")
        
        if matches:
            print("\n前3条比赛数据如下：")
            for i, match in enumerate(matches[:3]):
                print(f"\n比赛 {i+1}:")
                print(f"  ID: {match.get('match_id')}")
                print(f"  主队: {match.get('home_team')}")
                print(f"  客队: {match.get('away_team')}")
                print(f"  联赛: {match.get('league')}")
                print(f"  时间: {match.get('match_time')}")
                print(f"  赔率(主胜): {match.get('odds_home_win')}")
                print(f"  赔率(平局): {match.get('odds_draw')}")
                print(f"  赔率(客胜): {match.get('odds_away_win')}")
                print(f"  来源: {match.get('source', 'unknown')}")
        else:
            print("通过 advanced_crawler 未获取到任何比赛数据")
    except Exception as e:
        print(f"advanced_crawler 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 测试使用sporttery_scraper
    print("\n=== 测试 sporttery_scraper ===")
    try:
        async with sporttery_scraper as scraper:
            matches = await scraper.get_recent_matches(3)
            print(f"通过 sporttery_scraper 获取到 {len(matches)} 条比赛数据")
            
            if matches:
                print("\n前3条比赛数据如下：")
                for i, match in enumerate(matches[:3]):
                    print(f"\n比赛 {i+1}:")
                    print(f"  ID: {match.get('match_id')}")
                    print(f"  主队: {match.get('home_team')}")
                    print(f"  客队: {match.get('away_team')}")
                    print(f"  联赛: {match.get('league')}")
                    print(f"  时间: {match.get('match_time')}")
                    print(f"  赔率(主胜): {match.get('odds_home_win')}")
                    print(f"  赔率(平局): {match.get('odds_draw')}")
                    print(f"  赔率(客胜): {match.get('odds_away_win')}")
                    print(f"  来源: {match.get('source', 'unknown')}")
            else:
                print("通过 sporttery_scraper 未获取到任何比赛数据")
    except Exception as e:
        print(f"sporttery_scraper 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 测试热门比赛获取
    print("\n=== 测试热门比赛获取 ===")
    try:
        async with sporttery_scraper as scraper:
            popular_matches = await scraper.get_popular_matches()
            print(f"通过 sporttery_scraper 获取到 {len(popular_matches)} 条热门比赛数据")
            
            if popular_matches:
                print("\n热门比赛数据如下：")
                for i, match in enumerate(popular_matches):
                    print(f"\n热门比赛 {i+1}:")
                    print(f"  ID: {match.get('match_id')}")
                    print(f"  主队: {match.get('home_team')}")
                    print(f"  客队: {match.get('away_team')}")
                    print(f"  联赛: {match.get('league')}")
                    print(f"  热门程度: {match.get('popularity')}")
    except Exception as e:
        print(f"热门比赛获取测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 测试趋势话题获取
    print("\n=== 测试趋势话题获取 ===")
    try:
        async with sporttery_scraper as scraper:
            trending_topics = await scraper.get_trending_topics()
            print(f"通过 sporttery_scraper 获取到 {len(trending_topics)} 个趋势话题")
            
            if trending_topics:
                print("\n趋势话题数据如下：")
                for i, topic in enumerate(trending_topics):
                    print(f"\n话题 {i+1}:")
                    print(f"  标题: {topic.get('title')}")
                    print(f"  内容: {topic.get('content')}")
                    print(f"  来源: {topic.get('source')}")
                    print(f"  重要性: {topic.get('importance')}")
                    print(f"  类型: {topic.get('topic_type')}")
    except Exception as e:
        print(f"趋势话题获取测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n测试完成")


if __name__ == "__main__":
    # 运行测试
    result = asyncio.run(test_improved_sporttery_crawler())
    print(f"\n测试完成")