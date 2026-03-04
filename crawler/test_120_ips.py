"""
测试从89ip.cn获取120个IP
"""
import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.ip_proxy import IPProxyManager


def test_fetch_120_ips():
    """
    测试从89ip.cn获取120个IP的功能
    """
    print("="*60)
    print("测试从89ip.cn获取120个IP的功能")
    print("="*60)
    
    # 创建IP代理管理器
    manager = IPProxyManager()
    
    print(f"初始代理池大小: {len(manager.proxy_list)}")
    print(f"预设IP数量: {len(manager.preset_ips)}")
    
    # 尝试刷新代理池到120个
    print(f"\n正在尝试刷新代理池到120个IP...")
    start_time = time.time()
    
    manager.refresh_proxy_pool(count=120)
    
    elapsed_time = time.time() - start_time
    print(f"刷新完成，耗时: {elapsed_time:.2f}秒")
    print(f"当前代理池大小: {len(manager.proxy_list)}")
    
    if len(manager.proxy_list) >= 120:
        print(f"✓ 成功获取到 {len(manager.proxy_list)} 个IP，达到目标数量")
    else:
        print(f"⚠ 当前有 {len(manager.proxy_list)} 个IP，少于目标数量120个")
        print(f"  这可能是由于89ip.cn网站的反爬虫机制限制了IP获取数量")
    
    # 显示统计信息
    stats = manager.get_proxy_statistics()
    print(f"\n代理池统计信息:")
    print(f"  总数量: {stats['total_count']}")
    print(f"  地区分布: {stats['provinces_distribution']}")
    print(f"  运营商分布: {stats['operators_distribution']}")
    
    # 显示前20个和后10个IP作为示例
    print(f"\n前20个IP示例:")
    for i, proxy in enumerate(manager.proxy_list[:20]):
        source = "网站" if proxy not in manager.preset_ips else "预设"
        print(f"  {i+1:2d}. {proxy['ip']}:{proxy['port']} ({source})")
    
    if len(manager.proxy_list) > 20:
        print(f"\n后10个IP示例:")
        for i, proxy in enumerate(manager.proxy_list[-10:], start=len(manager.proxy_list)-9):
            source = "网站" if proxy not in manager.preset_ips else "预设"
            print(f"  {i:2d}. {proxy['ip']}:{proxy['port']} ({source})")
    
    print(f"\n测试完成!")
    return len(manager.proxy_list)


if __name__ == "__main__":
    count = test_fetch_120_ips()
    if count >= 120:
        print(f"\n结果: 成功获取 {count} 个IP，达到目标要求")
    else:
        print(f"\n结果: 只获取到 {count} 个IP")
        print(f"由于网站反爬虫机制，可能无法获取更多IP")
        print(f"但是当前IP池仍然可以正常使用")