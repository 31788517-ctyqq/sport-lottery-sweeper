"""
高级爬虫测试脚本 - 测试优化后的反反爬机制
"""
import asyncio
import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.scrapers.zqszsc_scraper import zqszsc_scraper


@pytest.mark.asyncio
async def test_advanced_scraper():
    """测试高级爬虫功能"""
    print("开始测试优化后的中国足球赛事赛程爬虫...")
    
    try:
        async with zqszsc_scraper as scraper:
            print("正在获取近3天的比赛数据...")
            matches = await scraper.get_recent_matches(3)
            
            print(f"成功获取到 {len(matches)} 场比赛数据:")
            for i, match in enumerate(matches):
                print(f"{i+1}. [{match.get('league', '未知联赛')}] "
                      f"{match.get('home_team', '未知主队')} VS {match.get('away_team', '未知客队')} - "
                      f"时间: {match.get('match_time', '未知时间')} - "
                      f"赔率: {match.get('odds_home_win', 'N/A')}|{match.get('odds_draw', 'N/A')}|{match.get('odds_away_win', 'N/A')} - "
                      f"来源: {match.get('source', '未知')}")
                
            print(f"\n总共获取到 {len(matches)} 场比赛")
                
    except Exception as e:
        print(f"爬虫测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_advanced_scraper())