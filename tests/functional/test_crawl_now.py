"""测试爬虫"""
import asyncio
import sys
import io

# 设置标准输出为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from backend.scrapers.sources.sporttery import SportteryScraper
from backend.scrapers.core.engine import ScraperEngine

async def main():
    print("="*80)
    print("测试从竞彩官网爬取近三天比赛数据")
    print("="*80)
    
    # 创建引擎和爬虫
    async with ScraperEngine() as engine:
        scraper = SportteryScraper(engine)
        
        print(f"\n数据源: {scraper.get_source_name()}")
        print("开始爬取...\n")
        
        # 获取比赛数据
        matches = await scraper.get_matches(days=3)
        
        print(f"\n[OK] 获取到 {len(matches)} 场比赛")
        
        # 检查是否是模拟数据
        if matches and matches[0].get('is_mock'):
            print("[WARNING]  当前使用模拟数据 (真实API未配置)")
        
        # 显示前5场比赛
        print("\n" + "-"*80)
        print("前5场比赛:")
        print("-"*80)
        
        for i, match in enumerate(matches[:5], 1):
            print(f"\n{i}. {match['home_team']} vs {match['away_team']}")
            print(f"   联赛: {match['league']}")
            print(f"   时间: {match['match_time']}")
            print(f"   赔率: {match['odds_home_win']:.2f} / {match['odds_draw']:.2f} / {match['odds_away_win']:.2f}")
        
        # 统计信息
        print("\n" + "="*80)
        print("统计信息")
        print("="*80)
        
        # 按联赛分组
        leagues = {}
        for match in matches:
            league = match['league']
            leagues[league] = leagues.get(league, 0) + 1
        
        print(f"\n联赛分布 (共{len(leagues)}个联赛):")
        for league, count in sorted(leagues.items(), key=lambda x: -x[1])[:10]:
            print(f"   {league}: {count}场")
        
        # 引擎统计
        stats = engine.get_stats()
        print(f"\n引擎统计:")
        print(f"   总请求: {stats['total_requests']}")
        print(f"   成功率: {stats.get('success_rate', 0):.1f}%")
        
        print("\n" + "="*80)
        print("测试完成")
        print("="*80)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n[ERROR] 错误: {e}")
        import traceback
        traceback.print_exc()
