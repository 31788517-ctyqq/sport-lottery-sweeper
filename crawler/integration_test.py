"""
IP代理模块与爬虫系统集成测试
验证IP代理模块是否成功集成到爬虫系统中
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.scrapers.coordinator import get_coordinator
from crawler.ip_proxy import IPProxyManager
from backend.scrapers.core.enhanced_engine import get_enhanced_engine


async def test_ip_proxy_integration():
    """
    测试IP代理模块与爬虫系统的集成
    """
    print("=== 开始测试IP代理模块与爬虫系统的集成 ===\n")
    
    # 1. 测试IP代理管理器
    print("1. 测试IP代理管理器:")
    ip_manager = IPProxyManager()
    print(f"   预设IP总数: {len(ip_manager.preset_ips)}")
    
    # 验证部分预设IP
    valid_count = 0
    for i, proxy in enumerate(ip_manager.preset_ips[:5]):
        is_valid = ip_manager.validate_proxy(proxy, timeout=5)
        status = "✓ 可用" if is_valid else "✗ 不可用"
        print(f"   {i+1}. {proxy['ip']}:{proxy['port']} - {status}")
        if is_valid:
            valid_count += 1
    
    print(f"   验证结果: {valid_count}/5 个预设IP可用\n")
    
    # 2. 测试增强型引擎
    print("2. 测试增强型爬虫引擎:")
    engine = await get_enhanced_engine()
    stats = engine.get_stats()
    print(f"   引擎统计: {stats}\n")
    
    # 3. 测试爬虫协调器
    print("3. 测试爬虫协调器:")
    coordinator = await get_coordinator()
    coord_stats = coordinator.get_stats()
    print(f"   协调器统计: 引擎活跃代理数 = {coord_stats['engine_stats']['active_proxies']}")
    
    # 4. 测试使用代理获取数据
    print("\n4. 测试使用代理获取数据:")
    try:
        matches = await coordinator.get_matches(days=1, sources=['mock'])
        print(f"   从模拟源获取到 {len(matches)} 场比赛")
    except Exception as e:
        print(f"   获取数据失败: {e}")
    
    # 5. 验证代理是否真正被使用
    print("\n5. 验证代理使用情况:")
    initial_stats = engine.get_stats()
    print(f"   当前活跃代理数: {initial_stats['active_proxies']}")
    print(f"   总请求数: {initial_stats['total_requests']}")
    print(f"   成功请求数: {initial_stats['successful_requests']}")
    
    print("\n=== 集成测试完成 ===")


def test_basic_ip_proxy_functionality():
    """
    测试IP代理模块的基本功能
    """
    print("=== 测试IP代理模块基本功能 ===\n")
    
    manager = IPProxyManager()
    
    print(f"预设IP总数: {len(manager.preset_ips)}")
    
    # 获取随机代理
    random_proxy = manager.get_random_proxy()
    if random_proxy:
        print(f"随机代理: {random_proxy['ip']}:{random_proxy['port']}")
    else:
        print("未能获取随机代理")
    
    # 获取有效代理
    valid_proxies = manager.get_valid_proxies(count=3)
    print(f"获取到 {len(valid_proxies)} 个有效代理")
    
    for i, proxy in enumerate(valid_proxies[:3]):
        print(f"  {i+1}. {proxy['ip']}:{proxy['port']}")
    
    print("\n=== 基本功能测试完成 ===\n")


if __name__ == "__main__":
    print("开始执行IP代理模块与爬虫系统集成测试...\n")
    
    # 测试基本功能
    test_basic_ip_proxy_functionality()
    
    # 运行异步测试
    asyncio.run(test_ip_proxy_integration())
    
    print("\n所有测试完成!")