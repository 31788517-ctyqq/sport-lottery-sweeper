"""
全面测试从89ip.cn获取30个IP的功能
结合预设IP和动态获取IP
"""
import sys
import os
import time
import random

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.ip_proxy import IPProxyManager


def comprehensive_test_30_ips():
    """
    全面测试获取30个IP的功能
    """
    print("="*60)
    print("全面测试从89ip.cn获取30个IP的功能")
    print("="*60)
    
    # 创建IP代理管理器
    manager = IPProxyManager()
    
    print(f"初始代理池大小: {len(manager.proxy_list)}")
    print(f"预设IP数量: {len(manager.preset_ips)}")
    
    # 测试获取有效代理
    print(f"\n正在尝试获取30个有效IP...")
    
    # 首先尝试验证预设IP中可用的
    print("\n正在验证预设IP...")
    valid_presets = []
    for i, preset_ip in enumerate(manager.preset_ips):
        if len(valid_presets) >= 30:
            break
        if manager.validate_proxy(preset_ip):
            valid_presets.append(preset_ip)
            print(f"✓ 预设IP验证通过: {preset_ip['ip']}:{preset_ip['port']}")
        else:
            print(f"✗ 预设IP验证失败: {preset_ip['ip']}:{preset_ip['port']}")
        
        # 添加小延时，避免请求过于频繁
        if i % 10 == 0:
            time.sleep(0.5)
    
    print(f"\n从预设IP中获取到 {len(valid_presets)} 个有效IP")
    
    # 如果预设IP不足30个，尝试从网站获取更多
    if len(valid_presets) < 30:
        print(f"\n预设IP不足30个，正在尝试从网站获取更多IP...")
        remaining_count = 30 - len(valid_presets)
        
        # 尝试从网站获取剩余数量的IP
        fresh_proxies = manager.fetch_multiple_pages(1, 3)
        print(f"从网站获取到 {len(fresh_proxies)} 个原始IP")
        
        # 验证从网站获取的IP
        valid_fresh = []
        for proxy in fresh_proxies:
            if len(valid_fresh) >= remaining_count:
                break
            if manager.validate_proxy(proxy):
                # 确保不重复添加已有的IP
                if not any(p['ip'] == proxy['ip'] and p['port'] == proxy['port'] for p in valid_presets):
                    valid_fresh.append(proxy)
                    print(f"✓ 网站IP验证通过: {proxy['ip']}:{proxy['port']}")
        
        print(f"从网站获取到 {len(valid_fresh)} 个有效IP")
        
        # 合并预设IP和网站IP
        all_valid = valid_presets + valid_fresh
    else:
        all_valid = valid_presets[:30]
    
    print(f"\n总共获取到 {len(all_valid)} 个有效IP")
    
    if len(all_valid) >= 30:
        print("✓ 成功获取至少30个有效IP")
    else:
        print(f"⚠ 只获取到 {len(all_valid)} 个有效IP，少于目标数量30个")
        print("这可能是由于89ip.cn网站的反爬虫机制导致无法获取网站IP")
    
    # 显示获取到的所有IP
    print(f"\n获取到的IP列表:")
    for i, proxy in enumerate(all_valid):
        source = "预设" if any(p['ip'] == proxy['ip'] and p['port'] == proxy['port'] for p in manager.preset_ips) else "网站"
        print(f"{i+1:2d}. {proxy['ip']}:{proxy['port']} ({source})")
    
    # 更新代理池
    manager.proxy_list = all_valid
    print(f"\n已更新代理池，当前代理池大小: {len(manager.proxy_list)}")
    
    # 显示统计信息
    stats = manager.get_proxy_statistics()
    print(f"\n代理池统计信息:")
    print(f"  总数量: {stats['total_count']}")
    print(f"  地区分布: {stats['provinces_distribution']}")
    print(f"  运营商分布: {stats['operators_distribution']}")
    
    # 测试随机获取代理功能
    print(f"\n测试随机获取代理功能:")
    for i in range(3):
        random_proxy = manager.get_random_proxy()
        if random_proxy:
            print(f"  {i+1}. 随机获取: {random_proxy['ip']}:{random_proxy['port']}")
        else:
            print(f"  {i+1}. 随机获取: 无可用代理")
    
    print("\n" + "="*60)
    print("测试完成!")
    print("="*60)
    
    return len(all_valid)


if __name__ == "__main__":
    count = comprehensive_test_30_ips()
    if count >= 30:
        print(f"\n结果: 成功获取 {count} 个有效IP，达到目标要求")
    else:
        print(f"\n结果: 只获取到 {count} 个有效IP，未达到30个的目标")
        print("建议: 继续使用现有的预设IP，它们构成了代理池的主要部分")