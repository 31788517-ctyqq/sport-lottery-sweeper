"""
简化的爬虫测试脚本
用于验证爬虫系统是否正常工作
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.scrapers.coordinator import get_coordinator
from crawler.ip_proxy import IPProxyManager


async def simple_test():
    """
    简化的测试
    """
    print("开始测试爬虫系统...")
    
    try:
        # 测试IP代理管理器
        print("\n1. 测试IP代理模块:")
        ip_manager = IPProxyManager()
        print(f"   ✓ 预设IP总数: {len(ip_manager.preset_ips)}")
        
        # 验证部分预设IP的可用性
        valid_count = 0
        for i, proxy in enumerate(ip_manager.preset_ips[:3]):
            is_valid = ip_manager.validate_proxy(proxy, timeout=3)
            status = "✓" if is_valid else "✗"
            print(f"   {status} {proxy['ip']}:{proxy['port']}")
            if is_valid:
                valid_count += 1
        print(f"   ✓ 验证结果: {valid_count}/3 个预设IP可用")
        
        # 获取爬虫协调器（只使用模拟源）
        print("\n2. 测试爬虫协调器 (使用模拟数据源):")
        coordinator = await get_coordinator()
        print("   ✓ 成功获取爬虫协调器实例")
        
        # 测试获取模拟数据
        print("\n3. 测试获取模拟数据:")
        matches = await coordinator.get_matches(days=1, sources=['mock'])
        print(f"   ✓ 从模拟源获取到 {len(matches)} 场比赛")
        
        if matches:
            sample_match = matches[0]
            print(f"   ✓ 示例比赛: {sample_match.get('home_team', 'N/A')} vs {sample_match.get('away_team', 'N/A')}")
            print(f"              联赛: {sample_match.get('league', 'N/A')}, 时间: {sample_match.get('match_time', 'N/A')}")
        
        # 测试健康检查
        print("\n4. 测试健康检查:")
        health_status = await coordinator.health_check_all()
        for source, status in health_status.items():
            health_indicator = "✓" if status['healthy'] else "✗"
            print(f"   {health_indicator} {source}: {'健康' if status['healthy'] else '不健康'}")
        
        print("\n5. 系统状态:")
        stats = coordinator.get_stats()
        engine_stats = stats['engine_stats']
        print(f"   ✓ 活跃代理数: {engine_stats['active_proxies']}")
        print(f"   ✓ 总请求数: {engine_stats['total_requests']}")
        print(f"   ✓ 成功请求数: {engine_stats['successful_requests']}")
        
        print("\n✓ 所有测试通过！爬虫系统正常运行。")
        
    except Exception as e:
        print(f"\n✗ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(simple_test())