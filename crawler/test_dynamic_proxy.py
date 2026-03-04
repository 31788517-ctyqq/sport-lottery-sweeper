"""
测试动态IP代理功能
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.ip_proxy import IPProxyManager


def test_fetch_from_89ip():
    """
    测试从89ip.cn获取IP代理的功能
    """
    print("开始测试从89ip.cn获取IP代理的功能...")
    
    manager = IPProxyManager()
    
    print(f"初始代理池大小: {len(manager.proxy_list)}")
    print(f"预设IP数量: {len(manager.preset_ips)}")
    
    # 测试从网站获取IP
    print("\n正在从第1页获取代理IP...")
    page_1_proxies = manager.fetch_proxies_from_page(1)
    print(f"从第1页获取到 {len(page_1_proxies)} 个代理IP")
    
    if page_1_proxies:
        print("前3个IP示例:")
        for i, proxy in enumerate(page_1_proxies[:3]):
            print(f"  {i+1}. {proxy['ip']}:{proxy['port']}")
    
    # 测试获取多页
    print("\n正在从多页获取代理IP...")
    multi_page_proxies = manager.fetch_multiple_pages(1, 2)
    print(f"从多页获取到 {len(multi_page_proxies)} 个代理IP")
    
    # 测试验证代理
    print("\n正在验证部分代理的有效性...")
    valid_proxies = manager.get_valid_proxies(count=3, page_range=(1, 2))
    print(f"获取到 {len(valid_proxies)} 个有效代理")
    
    if valid_proxies:
        print("有效代理示例:")
        for i, proxy in enumerate(valid_proxies[:3]):
            print(f"  {i+1}. {proxy['ip']}:{proxy['port']}")
    
    # 测试随机获取代理
    print("\n测试随机获取代理...")
    random_proxy = manager.get_random_proxy()
    if random_proxy:
        print(f"随机代理: {random_proxy['ip']}:{random_proxy['port']}")
    
    # 测试刷新代理池
    print("\n正在刷新代理池...")
    manager.refresh_proxy_pool(count=5)
    print(f"刷新后代理池大小: {len(manager.proxy_list)}")
    
    # 获取统计信息
    stats = manager.get_proxy_statistics()
    print(f"\n代理池统计信息:")
    print(f"  总数量: {stats['total_count']}")
    print(f"  地区分布: {stats['provinces_distribution']}")
    print(f"  运营商分布: {stats['operators_distribution']}")
    
    print("\n测试完成!")


if __name__ == "__main__":
    test_fetch_from_89ip()