"""
测试高级Selenium爬虫功能
"""
import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.scrapers.sources.advanced_five_hundred_selenium_scraper import (
    AdvancedFiveHundredSeleniumScraper,
    scrape_five_hundred_jczq_advanced_selenium
)


def test_advanced_selenium_scraper():
    """
    测试高级Selenium爬虫
    """
    print("="*60)
    print("开始测试高级Selenium版500彩票网竞彩足球爬虫")
    print("="*60)
    
    print(f"\n1. 初始化高级Selenium爬虫...")
    scraper = AdvancedFiveHundredSeleniumScraper()
    
    print(f"\n2. 开始爬取数据...")
    start_time = datetime.now()
    matches = scraper.get_matches(days=3)
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"[OK] 爬取完成，耗时: {duration:.2f}秒")
    print(f"[ANALYTICS] 获取到 {len(matches)} 场比赛")
    
    if matches:
        print(f"\n🏆 按联赛分类:")
        leagues = {}
        for match in matches:
            league = match.get('league', '未知联赛')
            if league not in leagues:
                leagues[league] = 0
            leagues[league] += 1
        
        for league, count in sorted(leagues.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {league}: {count} 场")
        
        print(f"\n[LOG] 前5场比赛详情:")
        for i, match in enumerate(matches[:5]):
            print(f"   {i+1}. [{match.get('match_id', '未知ID')}] {match.get('league', '未知联赛')}")
            print(f"      {match.get('home_team', '未知主队')} VS {match.get('away_team', '未知客队')}")
            print(f"      时间: {match.get('match_time', '未知时间')}")
            print(f"      赔率: 主胜 {match.get('odds_home_win', 0):.2f} | 平 {match.get('odds_draw', 0):.2f} | 客胜 {match.get('odds_away_win', 0):.2f}")
            print()
    else:
        print(f"\n[WARNING]  没有获取到任何比赛数据")
        print("[HINT] 可能原因:")
        print("   - 500彩票网结构发生变化")
        print("   - 网络连接问题")
        print("   - 反爬虫机制")
        print("   - 当前时间段没有比赛安排")
        print("   - 需要等待页面完全加载")
    
    # 测试机器学习模型功能
    print(f"\n3. 测试机器学习模型功能...")
    recommendation = scraper.ml_model.get_optimal_timing_recommendation()
    print(f"   最佳访问时间推荐: {recommendation['recommended_hour']}点")
    print(f"   推荐理由: {recommendation['reason']}")
    
    # 测试便捷函数
    print(f"\n4. 测试便捷函数...")
    start_time = datetime.now()
    matches_fn = scrape_five_hundred_jczq_advanced_selenium(days=1)
    end_time = datetime.now()
    duration_fn = (end_time - start_time).total_seconds()
    
    print(f"[OK] 便捷函数完成，耗时: {duration_fn:.2f}秒")
    print(f"[ANALYTICS] 便捷函数获取到 {len(matches_fn)} 场比赛")
    
    scraper.close()
    
    print(f"\n{'='*60}")
    print("高级Selenium爬虫测试完成")
    print(f"{'='*60}")


if __name__ == "__main__":
    test_advanced_selenium_scraper()