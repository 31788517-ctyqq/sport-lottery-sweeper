"""
测试改进后的500彩票网爬虫
"""
import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.scrapers.sources.five_hundred_scraper import FiveHundredScraper, scrape_five_hundred_jczq
from backend.scrapers.sources.five_hundred_proxy_scraper import FiveHundredProxyScraper, scrape_five_hundred_jczq_with_proxy


async def test_improved_scraper():
    """
    测试改进后的500彩票网爬虫
    """
    print("="*60)
    print("开始测试改进后的500彩票网竞彩足球爬虫")
    print("="*60)
    
    # 测试普通版爬虫
    print(f"\n1. 测试普通版爬虫...")
    scraper_normal = FiveHundredScraper()
    
    start_time = datetime.now()
    matches_normal = await scraper_normal.get_matches(days=3)
    end_time = datetime.now()
    duration_normal = (end_time - start_time).total_seconds()
    
    print(f"✅ 普通版爬虫完成，耗时: {duration_normal:.2f}秒")
    print(f"📊 获取到 {len(matches_normal)} 场比赛")
    
    if matches_normal:
        print(f"\n🏆 普通版按联赛分类:")
        leagues = {}
        for match in matches_normal:
            league = match.get('league', '未知联赛')
            if league not in leagues:
                leagues[league] = 0
            leagues[league] += 1
        
        for league, count in sorted(leagues.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {league}: {count} 场")
    
    await scraper_normal.close()
    
    # 测试代理版爬虫
    print(f"\n2. 测试代理版爬虫...")
    scraper_proxy = FiveHundredProxyScraper()
    
    start_time = datetime.now()
    matches_proxy = await scraper_proxy.get_matches(days=3)
    end_time = datetime.now()
    duration_proxy = (end_time - start_time).total_seconds()
    
    print(f"✅ 代理版爬虫完成，耗时: {duration_proxy:.2f}秒")
    print(f"📊 获取到 {len(matches_proxy)} 场比赛")
    
    if matches_proxy:
        print(f"\n🏆 代理版按联赛分类:")
        leagues = {}
        for match in matches_proxy:
            league = match.get('league', '未知联赛')
            if league not in leagues:
                leagues[league] = 0
            leagues[league] += 1        
        for league, count in sorted(leagues.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {league}: {count} 场")
    
    await scraper_proxy.close()
    
    # 测试便捷函数
    print(f"\n3. 测试便捷函数...")
    start_time = datetime.now()
    matches_fn = await scrape_five_hundred_jczq(days=1)
    end_time = datetime.now()
    duration_fn = (end_time - start_time).total_seconds()
    
    print(f"✅ 普通版便捷函数完成，耗时: {duration_fn:.2f}秒")
    print(f"📊 获取到 {len(matches_fn)} 场比赛")
    
    start_time = datetime.now()
    matches_proxy_fn = await scrape_five_hundred_jczq_with_proxy(days=1)
    end_time = datetime.now()
    duration_proxy_fn = (end_time - start_time).total_seconds()
    
    print(f"✅ 代理版便捷函数完成，耗时: {duration_proxy_fn:.2f}秒")
    print(f"📊 获取到 {len(matches_proxy_fn)} 场比赛")
    
    # 比较结果
    print(f"\n4. 结果对比:")
    print(f"   普通版获取: {len(matches_normal)} 场")
    print(f"   代理版获取: {len(matches_proxy)} 场")
    print(f"   普通版便捷函数: {len(matches_fn)} 场")
    print(f"   代理版便捷函数: {len(matches_proxy_fn)} 场")
    
    # 如果获取到了比赛数据，显示前几场比赛
    if matches_normal or matches_proxy:
        print(f"\n5. 比赛详情 (取数据较多的版本):")
        matches_to_show = matches_normal if len(matches_normal) >= len(matches_proxy) else matches_proxy
        for i, match in enumerate(matches_to_show[:5]):
            print(f"   {i+1}. [{match.get('match_id', '未知ID')}] {match.get('league', '未知联赛')}")
            print(f"      {match.get('home_team', '未知主队')} VS {match.get('away_team', '未知客队')}")
            print(f"      时间: {match.get('match_time', '未知时间')}")
            print(f"      赔率: 主胜 {match.get('odds_home_win', 0):.2f} | 平 {match.get('odds_draw', 0):.2f} | 客胜 {match.get('odds_away_win', 0):.2f}")
            print()
    else:
        print(f"\n5. 提示:")
        print("   - 当前可能没有即将进行的比赛")
        print("   - 或者反爬虫机制仍然有效阻挡了爬取")
        print("   - 建议尝试使用Selenium版爬虫或更换IP代理")
    
    print(f"\n{'='*60}")
    print("测试完成")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(test_improved_scraper())