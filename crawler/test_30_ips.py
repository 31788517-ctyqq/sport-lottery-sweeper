"""
测试从89ip.cn爬取30个IP
"""
import sys
import os
import asyncio

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.ip_proxy import IPProxyManager


def test_fetch_30_ips():
    """
    测试从89ip.cn爬取30个IP的功能
    """
    print("开始测试从89ip.cn爬取30个IP的功能...")
    
    # 创建IP代理管理器
    manager = IPProxyManager()
    
    print(f"初始代理池大小: {len(manager.proxy_list)}")
    print(f"预设IP数量: {len(manager.preset_ips)}")
    
    # 尝试从网站获取IP
    print("\n正在从89ip.cn获取IP...")
    
    # 先尝试从多页获取IP
    fresh_proxies = manager.fetch_multiple_pages(1, 3)
    print(f"从网站获取到 {len(fresh_proxies)} 个原始IP")
    
    # 验证这些IP
    valid_proxies = []
    for proxy in fresh_proxies:
        if len(valid_proxies) >= 30:
            break
        if manager.validate_proxy(proxy):
            valid_proxies.append(proxy)
            print(f"✓ 验证通过: {proxy['ip']}:{proxy['port']}")
        else:
            print(f"✗ 验证失败: {proxy['ip']}:{proxy['port']}")
    
    print(f"\n从网站获取的有效IP数量: {len(valid_proxies)}")
    
    # 如果网站IP不足30个，使用预设IP补足
    if len(valid_proxies) < 30:
        print(f"网站IP不足30个，尝试使用预设IP补足...")
        remaining_count = 30 - len(valid_proxies)
        
        for preset_ip in manager.preset_ips:
            if len(valid_proxies) >= 30:
                break
            # 检查这个IP是否已经在列表中
            if not any(p['ip'] == preset_ip['ip'] and p['port'] == preset_ip['port'] for p in valid_proxies):
                if manager.validate_proxy(preset_ip):
                    valid_proxies.append(preset_ip)
                    print(f"✓ 使用预设IP: {preset_ip['ip']}:{preset_ip['port']}")
    
    print(f"\n最终获取的有效IP数量: {len(valid_proxies)}")
    
    if len(valid_proxies) >= 30:
        print("✓ 成功获取至少30个有效IP")
    else:
        print(f"⚠ 只获取到 {len(valid_proxies)} 个有效IP，少于目标数量30个")
    
    # 显示前30个IP
    print(f"\n前30个IP列表:")
    for i, proxy in enumerate(valid_proxies[:30]):
        print(f"{i+1:2d}. {proxy['ip']}:{proxy['port']}")
    
    # 测试刷新代理池
    print(f"\n测试刷新代理池功能...")
    manager.proxy_list = valid_proxies[:30]  # 只保留前30个
    manager.refresh_proxy_pool(count=30)
    
    print(f"刷新后代理池大小: {len(manager.proxy_list)}")
    
    # 验证代理池统计信息
    stats = manager.get_proxy_statistics()
    print(f"\n代理池统计信息:")
    print(f"  总数量: {stats['total_count']}")
    print(f"  地区分布: {stats['provinces_distribution']}")
    print(f"  运营商分布: {stats['operators_distribution']}")
    
    print("\n测试完成!")


if __name__ == "__main__":
    test_fetch_30_ips()