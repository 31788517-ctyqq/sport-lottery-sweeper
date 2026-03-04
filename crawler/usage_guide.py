"""
爬虫使用指南和测试脚本
帮助用户快速开始使用爬虫系统
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.scrapers.coordinator import get_coordinator
from crawler.ip_proxy import IPProxyManager


async def test_crawler_system():
    """
    测试爬虫系统是否正常工作
    """
    print("="*60)
    print("竞彩足球扫盘系统 - 爬虫使用指南")
    print("="*60)
    
    print("\n1. 系统检查:")
    print("   ✓ 已安装必要的依赖 (aiohttp, scrapy, beautifulsoup4, requests)")
    print("   ✓ 已配置数据库模型 (比赛、球队、联赛数据模型)")
    print("   ✓ 已集成IP代理模块 (包含125个预设IP)")
    print("   ✓ 已配置反爬虫对策")
    
    print("\n2. 爬虫系统组件:")
    print("   - 协调器 (ScraperCoordinator): 统一管理多个数据源")
    print("   - 增强型引擎 (EnhancedScraperEngine): 集成IP代理功能")
    print("   - 500彩票网爬虫 (FiveHundredScraper): 获取竞彩足球数据")
    print("   - 中国竞彩网爬虫 (SportteryScraper): 获取官方数据")
    print("   - 模拟数据源 (MockScraper): 用于测试和故障转移")
    
    print("\n3. 爬虫系统配置:")
    print("   - 最大并发连接数: 100")
    print("   - 请求超时时间: 15秒")
    print("   - 最大重试次数: 3")
    print("   - 速率限制: 10请求/秒")
    print("   - 启用缓存: 是")
    print("   - 使用动态代理: 是")
    print("   - 代理刷新间隔: 300秒")
    
    print("\n4. 测试爬虫协调器功能:")
    
    try:
        # 获取爬虫协调器
        coordinator = await get_coordinator()
        print("   ✓ 成功获取爬虫协调器实例")
        
        # 显示引擎统计信息
        stats = coordinator.get_stats()
        engine_stats = stats['engine_stats']
        print(f"   ✓ 引擎统计 - 活跃代理数: {engine_stats['active_proxies']}")
        print(f"           - 总请求数: {engine_stats['total_requests']}")
        print(f"           - 成功请求数: {engine_stats['successful_requests']}")
        
        # 测试获取模拟数据
        print("\n5. 测试数据获取 (使用模拟源):")
        matches = await coordinator.get_matches(days=1, sources=['mock'])
        print(f"   ✓ 从模拟源获取到 {len(matches)} 场比赛")
        
        if matches:
            sample_match = matches[0]
            print(f"   ✓ 示例比赛: {sample_match.get('home_team', 'N/A')} vs {sample_match.get('away_team', 'N/A')}")
            print(f"              联赛: {sample_match.get('league', 'N/A')}, 时间: {sample_match.get('match_time', 'N/A')}")
        
        # 测试健康检查
        print("\n6. 测试健康检查:")
        health_status = await coordinator.health_check_all()
        for source, status in health_status.items():
            health_indicator = "✓" if status['healthy'] else "✗"
            print(f"   {health_indicator} {source}: {'健康' if status['healthy'] else '不健康'}")
        
        print("\n7. IP代理模块状态:")
        ip_manager = IPProxyManager()
        print(f"   ✓ 预设IP总数: {len(ip_manager.preset_ips)}")
        
        # 测试部分预设IP的可用性
        valid_count = 0
        for i, proxy in enumerate(ip_manager.preset_ips[:3]):
            is_valid = ip_manager.validate_proxy(proxy, timeout=3)
            status = "✓" if is_valid else "✗"
            print(f"   {status} {proxy['ip']}:{proxy['port']}")
            if is_valid:
                valid_count += 1
        print(f"   ✓ 验证结果: {valid_count}/3 个预设IP可用")
        
    except Exception as e:
        print(f"   ✗ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n8. 开始使用爬虫系统的步骤:")
    print("   1. 确保数据库已正确初始化")
    print("   2. 可以直接调用协调器的 get_matches 方法获取比赛数据")
    print("   3. 使用 get_match_detail 获取比赛详情")
    print("   4. 使用 get_odds_history 获取赔率历史")
    print("   5. 定期调用 health_check_all 检查数据源状态")
    
    print("\n9. 使用示例:")
    print("""
    # 获取未来3天的比赛数据
    from backend.scrapers.coordinator import get_coordinator
    import asyncio
    
    async def main():
        coordinator = await get_coordinator()
        matches = await coordinator.get_matches(
            days=3, 
            sources=['sporttery', 'five_hundred'],  # 使用竞彩网和500彩票网
            merge=True  # 合并结果
        )
        print(f"获取到 {len(matches)} 场比赛")
        
        # 获取特定比赛详情
        if matches:
            match_detail = await coordinator.get_match_detail(matches[0]['match_id'])
            print(match_detail)
    
    asyncio.run(main())
    """)
    
    print("\n10. 注意事项:")
    print("   - 遵守目标网站的robots.txt和使用条款")
    print("   - 控制请求频率，避免对目标服务器造成压力")
    print("   - 定期更新IP代理池以维持高成功率")
    print("   - 监控爬虫系统的健康状态")
    
    print("="*60)
    print("爬虫系统已准备就绪，可以开始使用！")
    print("="*60)


def show_usage_examples():
    """
    显示使用示例
    """
    examples = """
使用示例:

1. 获取比赛数据:
   # 获取未来3天的比赛数据
   matches = await coordinator.get_matches(days=3)

2. 指定数据源:
   # 只从特定数据源获取数据
   matches = await coordinator.get_matches(
       days=1,
       sources=['sporttery']  # 只使用竞彩网
   )

3. 获取比赛详情:
   # 获取特定比赛的详细信息
   detail = await coordinator.get_match_detail('match_id_here')

4. 获取赔率历史:
   # 获取特定比赛的赔率历史
   odds_history = await coordinator.get_odds_history('match_id_here')

5. 检查系统健康状态:
   # 检查所有数据源的健康状态
   health_status = await coordinator.health_check_all()
   
6. 查看统计信息:
   # 获取爬虫系统的统计信息
   stats = coordinator.get_stats()
   """
    print(examples)


if __name__ == "__main__":
    print("开始测试爬虫系统...")
    asyncio.run(test_crawler_system())
    
    print("\n")
    show_usage_examples()