"""
测试爬虫功能的脚本
"""
import asyncio
import sys
import os

# 添加项目路径到sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from backend.app.scrapers.sporttery_scraper import sporttery_scraper


async def test_scraper():
    print("开始测试竞彩网爬虫...")
    
    try:
        # 调用爬虫获取数据
        matches = await sporttery_scraper.get_recent_matches(3)
        
        print(f"成功获取到 {len(matches)} 条比赛数据")
        
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
        else:
            print("\n未获取到任何比赛数据，可能是使用了模拟数据或爬取失败")
        
        return matches
        
    except Exception as e:
        print(f"爬虫测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    # 运行测试
    result = asyncio.run(test_scraper())
    print(f"\n测试完成，共获取 {len(result)} 条数据")