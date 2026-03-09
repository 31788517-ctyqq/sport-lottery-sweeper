"""
测试500彩票网竞彩足球爬虫
"""
import asyncio
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.scrapers.sources.five_hundred_scraper import FiveHundredScraper, scrape_five_hundred_jczq


async def test_five_hundred_scraper():
    """
    测试500彩票网爬虫
    """
    print("="*60)
    print("开始测试500彩票网竞彩足球爬虫")
    print("="*60)
    
    # 创建爬虫实例
    scraper = FiveHundredScraper()
    
    print(f"开始爬取数据...")
    start_time = datetime.now()
    
    try:
        # 获取未来3天的比赛
        matches = await scraper.get_matches(days=3)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ 爬取完成，耗时: {duration:.2f}秒")
        print(f"📊 获取到 {len(matches)} 场比赛")
        
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
            
            print(f"\n📝 比赛详情 (前5场):")
            for i, match in enumerate(matches[:5]):
                print(f"   {i+1}. [{match.get('match_id', '未知ID')}] {match.get('league', '未知联赛')}")
                print(f"      {match.get('home_team', '未知主队')} VS {match.get('away_team', '未知客队')}")
                print(f"      时间: {match.get('match_time', '未知时间')}")
                print(f"      赔率: 主胜 {match.get('odds_home_win', 0):.2f} | 平 {match.get('odds_draw', 0):.2f} | 客胜 {match.get('odds_away_win', 0):.2f}")
                print()
            
            if len(matches) > 5:
                print(f"   ... 还有 {len(matches) - 5} 场比赛")
        else:
            print("⚠️  没有获取到任何比赛数据")
            print("💡 可能原因:")
            print("   - 500彩票网结构发生变化")
            print("   - 网络连接问题")
            print("   - 反爬虫机制")
            print("   - 当前时间段没有比赛安排")
        
        # 测试便捷函数
        print(f"\n🧪 测试便捷函数...")
        matches_fn = await scrape_five_hundred_jczq(days=1)
        print(f"✅ 便捷函数获取到 {len(matches_fn)} 场比赛")
        
    except Exception as e:
        print(f"❌ 爬取过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭爬虫
        await scraper.close()
    
    print(f"\n{'='*60}")
    print("测试完成")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(test_five_hundred_scraper())