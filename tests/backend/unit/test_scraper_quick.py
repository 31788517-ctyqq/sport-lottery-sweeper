#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速测试爬虫获取比赛数据
"""

import asyncio
import json
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 导入爬虫
from backend.app.scrapers.sporttery_scraper import SportteryScraper


async def test_get_recent_matches():
    """测试获取最近3天的比赛数据"""
    print("\n" + "="*60)
    print("测试：获取最近3天的比赛数据")
    print("="*60)
    
    async with SportteryScraper() as scraper:
        matches = await scraper.get_recent_matches(days_ahead=3)
        
        print(f"\n✓ 获取到 {len(matches)} 场比赛\n")
        
        if matches:
            # 显示前5场比赛的详细信息
            print("前5场比赛详细信息：\n")
            for i, match in enumerate(matches[:5], 1):
                print(f"比赛 {i}:")
                print(f"  主队: {match.get('home_team', 'N/A')}")
                print(f"  客队: {match.get('away_team', 'N/A')}")
                print(f"  联赛: {match.get('league', 'N/A')}")
                print(f"  时间: {match.get('match_date', 'N/A')}")
                print(f"  主胜赔率: {match.get('odds_home_win', 'N/A')}")
                print(f"  平局赔率: {match.get('odds_draw', 'N/A')}")
                print(f"  客胜赔率: {match.get('odds_away_win', 'N/A')}")
                print(f"  热度: {match.get('popularity', 'N/A')}")
                print()
            
            # 统计信息
            print("\n统计信息：")
            print(f"  总比赛数: {len(matches)}")
            
            # 按联赛统计
            leagues = {}
            for match in matches:
                league = match.get('league', '未知')
                leagues[league] = leagues.get(league, 0) + 1
            
            print(f"  联赛分布:")
            for league, count in sorted(leagues.items(), key=lambda x: x[1], reverse=True):
                print(f"    - {league}: {count}场")
            
            # 按日期统计
            dates = {}
            for match in matches:
                date = match.get('match_date', '').split(' ')[0]
                dates[date] = dates.get(date, 0) + 1
            
            print(f"  日期分布:")
            for date in sorted(dates.keys()):
                print(f"    - {date}: {dates[date]}场")
            
            # 输出原始JSON（便于调试）
            print("\n原始JSON数据（前2场）:")
            print(json.dumps(matches[:2], indent=2, ensure_ascii=False))
            
            return True
        else:
            print("❌ 未获取到任何比赛数据")
            return False


async def test_get_popular_matches():
    """测试获取热门比赛"""
    print("\n" + "="*60)
    print("测试：获取热门比赛")
    print("="*60)
    
    async with SportteryScraper() as scraper:
        matches = await scraper.get_popular_matches()
        
        print(f"\n✓ 获取到 {len(matches)} 场热门比赛\n")
        
        if matches:
            for i, match in enumerate(matches[:5], 1):
                popularity = match.get('popularity', 0)
                print(f"{i}. {match.get('home_team')} vs {match.get('away_team')} - "
                      f"热度: {popularity}/100 - 时间: {match.get('match_date')}")
            
            return True
        else:
            print("❌ 未获取到热门比赛数据")
            return False


async def main():
    """主测试函数"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  体育竞彩网爬虫测试".center(58) + "║")
    print("║" + "  运行时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S").center(50) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        # 测试1：获取最近3天的比赛数据
        result1 = await test_get_recent_matches()
        
        # 测试2：获取热门比赛
        result2 = await test_get_popular_matches()
        
        # 总结
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        print(f"✓ 获取最近比赛: {'成功' if result1 else '失败'}")
        print(f"✓ 获取热门比赛: {'成功' if result2 else '失败'}")
        print("="*60 + "\n")
        
        if result1 and result2:
            print("✅ 所有测试通过！爬虫工作正常。\n")
        else:
            print("⚠️  部分测试失败，请检查日志。\n")
            
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
