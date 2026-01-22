#!/usr/bin/env python
"""
新爬虫测试脚本
用于验证重构后的爬虫模块是否正常工作
"""
import asyncio
import sys
import logging
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_engine():
    """测试爬虫引擎"""
    print("\n" + "="*60)
    print("测试1: 爬虫引擎基础功能")
    print("="*60)
    
    from backend.scrapers.core.engine import ScraperEngine
    
    async with ScraperEngine() as engine:
        # 测试HTTP请求
        print("\n📡 测试HTTP请求...")
        response = await engine.fetch('https://httpbin.org/get')
        print(f"✅ 状态码: {response['status']}")
        
        # 测试统计信息
        stats = engine.get_stats()
        print(f"\n📊 统计信息:")
        print(f"  总请求数: {stats['total_requests']}")
        print(f"  成功请求: {stats['successful_requests']}")
        print(f"  成功率: {stats.get('success_rate', 0)}%")


async def test_sporttery_scraper():
    """测试竞彩网爬虫"""
    print("\n" + "="*60)
    print("测试2: 竞彩网爬虫")
    print("="*60)
    
    from backend.scrapers.sources.sporttery import SportteryScraper
    
    async with SportteryScraper() as scraper:
        print(f"\n🌐 数据源: {scraper.get_source_name()}")
        
        # 测试获取比赛
        print("\n⚽ 获取比赛数据（未来3天）...")
        matches = await scraper.get_matches(3)
        print(f"✅ 获取到 {len(matches)} 场比赛")
        
        if matches:
            # 显示前3场比赛
            print("\n前3场比赛:")
            for i, match in enumerate(matches[:3], 1):
                print(f"\n  {i}. {match['home_team']} vs {match['away_team']}")
                print(f"     联赛: {match['league']}")
                print(f"     时间: {match['match_time']}")
                print(f"     赔率: {match['odds_home_win']} / {match['odds_draw']} / {match['odds_away_win']}")
                if match.get('is_mock'):
                    print(f"     ⚠️  模拟数据")
            
            # 测试获取详情
            print("\n\n📝 获取第一场比赛的详情...")
            match_id = matches[0]['match_id']
            detail = await scraper.get_match_detail(match_id)
            if detail:
                print(f"✅ 获取到比赛详情")
            
            # 测试获取赔率历史
            print("\n📈 获取赔率历史...")
            history = await scraper.get_odds_history(match_id)
            if history:
                print(f"✅ 获取到 {len(history)} 条赔率历史记录")


async def test_coordinator():
    """测试爬虫协调器"""
    print("\n" + "="*60)
    print("测试3: 爬虫协调器")
    print("="*60)
    
    from backend.scrapers.coordinator import ScraperCoordinator
    
    async with ScraperCoordinator() as coordinator:
        # 测试获取比赛（使用默认数据源）
        print("\n🎯 通过协调器获取比赛数据...")
        matches = await coordinator.get_matches(days=2)
        print(f"✅ 获取到 {len(matches)} 场比赛")
        
        # 测试健康检查
        print("\n❤️  健康检查...")
        health = await coordinator.health_check_all()
        print(f"\n数据源状态:")
        for source, status in health.items():
            healthy = "✅" if status.get('healthy') else "❌"
            response_time = status.get('response_time', 0)
            print(f"  {healthy} {source}: {response_time:.3f}s")
        
        # 测试统计信息
        print("\n📊 协调器统计:")
        stats = coordinator.get_stats()
        engine_stats = stats['engine_stats']
        print(f"  总请求: {engine_stats['total_requests']}")
        print(f"  成功率: {engine_stats.get('success_rate', 0):.1f}%")
        print(f"  缓存命中率: {engine_stats.get('cache_hit_rate', 0):.1f}%")


async def test_performance():
    """测试性能"""
    print("\n" + "="*60)
    print("测试4: 性能测试")
    print("="*60)
    
    import time
    from backend.scrapers.coordinator import ScraperCoordinator
    
    async with ScraperCoordinator() as coordinator:
        # 测试并发获取
        print("\n⚡ 测试并发获取性能...")
        
        start = time.time()
        
        # 并发获取3次
        tasks = [
            coordinator.get_matches(days=1),
            coordinator.get_matches(days=1),
            coordinator.get_matches(days=1),
        ]
        results = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start
        
        total_matches = sum(len(r) for r in results)
        print(f"✅ 并发3次请求完成")
        print(f"  总耗时: {elapsed:.2f}秒")
        print(f"  获取比赛: {total_matches} 场")
        print(f"  平均速度: {elapsed/3:.2f}秒/次")
        
        # 测试缓存效果
        print("\n💾 测试缓存效果...")
        
        # 第一次请求（无缓存）
        start = time.time()
        await coordinator.get_matches(days=1)
        time_no_cache = time.time() - start
        
        # 第二次请求（有缓存）
        start = time.time()
        await coordinator.get_matches(days=1)
        time_with_cache = time.time() - start
        
        speedup = time_no_cache / time_with_cache if time_with_cache > 0 else 0
        
        print(f"  无缓存: {time_no_cache:.3f}秒")
        print(f"  有缓存: {time_with_cache:.3f}秒")
        print(f"  加速比: {speedup:.1f}x")


async def main():
    """运行所有测试"""
    print("\n" + "🚀"*30)
    print("爬虫模块测试套件")
    print("🚀"*30)
    
    try:
        await test_engine()
        await test_sporttery_scraper()
        await test_coordinator()
        await test_performance()
        
        print("\n" + "="*60)
        print("✅ 所有测试通过！")
        print("="*60)
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
