"""爬取今天的比赛赛程"""
import asyncio
import sys
import io
import json
from datetime import datetime
from pathlib import Path

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from backend.scrapers.sources.sporttery import SportteryScraper
from backend.scrapers.core.engine import ScraperEngine


async def crawl_today():
    """爬取今天的比赛"""
    print("="*80)
    print("🎯 从竞彩官网爬取今天的比赛赛程")
    print("="*80)
    
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"\n📅 日期: {today}")
    print(f"⏰ 时间: {datetime.now().strftime('%H:%M:%S')}\n")
    
    # 创建爬虫
    async with ScraperEngine() as engine:
        scraper = SportteryScraper(engine)
        
        print(f"🌐 数据源: {scraper.get_source_name()}")
        print("⚡ 开始爬取...\n")
        
        # 获取今天的比赛（days=1表示今天）
        matches = await scraper.get_matches(days=1)
        
        if not matches:
            print("❌ 未获取到比赛数据")
            return
        
        # 筛选今天的比赛
        today_matches = []
        for match in matches:
            match_date = match['match_time'][:10] if isinstance(match['match_time'], str) else str(match['match_time'])[:10]
            if today in match_date:
                today_matches.append(match)
        
        # 如果没有精确匹配，显示所有数据
        if not today_matches:
            today_matches = matches
            print(f"⚠️  未找到今天的比赛，显示获取到的所有比赛")
        
        print("="*80)
        print(f"✅ 获取到 {len(today_matches)} 场比赛")
        print("="*80)
        
        # 检查数据来源
        is_mock = today_matches[0].get('is_mock', False) if today_matches else False
        if is_mock:
            print("\n⚠️  当前使用模拟数据")
            print("💡 真实数据需要正确的API参数，请参考 FINAL_TEST_REPORT.md\n")
        else:
            print("\n✅ 真实数据\n")
        
        # 按联赛分组
        leagues = {}
        for match in today_matches:
            league = match['league']
            if league not in leagues:
                leagues[league] = []
            leagues[league].append(match)
        
        # 显示统计
        print("📊 联赛统计:")
        print(f"   总联赛数: {len(leagues)}")
        print(f"   总比赛数: {len(today_matches)}\n")
        
        # 按联赛显示
        print("="*80)
        print("📋 比赛详情")
        print("="*80)
        
        match_num = 1
        for league, league_matches in sorted(leagues.items()):
            print(f"\n🏆 {league} ({len(league_matches)}场)")
            print("-"*80)
            
            # 按时间排序
            league_matches.sort(key=lambda x: x['match_time'])
            
            for match in league_matches:
                # 提取时间
                match_time = match['match_time']
                if isinstance(match_time, str):
                    time_str = match_time[11:16] if len(match_time) > 16 else match_time
                else:
                    time_str = str(match_time)[11:16]
                
                # 状态图标
                status = match.get('status', 'scheduled')
                status_icon = {
                    'scheduled': '⏰',
                    'live': '🔴',
                    'finished': '✅'
                }.get(status, '⚪')
                
                # 显示比赛
                print(f"\n{match_num}. {status_icon} {time_str} | {match['home_team']} vs {match['away_team']}")
                print(f"   赔率: 胜{match['odds_home_win']:.2f} 平{match['odds_draw']:.2f} 负{match['odds_away_win']:.2f}")
                print(f"   比分: {match.get('score', '-:-')} | 热度: {match.get('popularity', 0)}")
                
                match_num += 1
        
        # 保存数据
        output_file = Path('debug') / f'today_matches_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(today_matches, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*80)
        print(f"💾 数据已保存: {output_file}")
        print("="*80)
        
        # 引擎统计
        stats = engine.get_stats()
        print(f"\n📈 爬虫统计:")
        print(f"   请求数: {stats['total_requests']}")
        print(f"   成功率: {stats.get('success_rate', 0):.1f}%")
        print(f"   响应时间: {stats.get('avg_response_time', 0):.2f}秒")
        
        # 推荐的比赛
        print("\n" + "="*80)
        print("🔥 热门推荐")
        print("="*80)
        
        # 按热度排序
        hot_matches = sorted(today_matches, key=lambda x: x.get('popularity', 0), reverse=True)[:5]
        
        for i, match in enumerate(hot_matches, 1):
            print(f"\n{i}. {match['home_team']} vs {match['away_team']}")
            print(f"   联赛: {match['league']} | 热度: {match.get('popularity', 0)}")
            print(f"   赔率: {match['odds_home_win']:.2f} / {match['odds_draw']:.2f} / {match['odds_away_win']:.2f}")


async def main():
    print("\n" + "⚽"*40)
    print("竞彩网今日赛程爬虫")
    print("⚽"*40 + "\n")
    
    try:
        await crawl_today()
        
        print("\n" + "="*80)
        print("✅ 爬取完成")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ 爬取失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
