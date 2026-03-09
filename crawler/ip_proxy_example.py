"""
IP代理模块使用示例
演示如何使用IPProxyManager获取和使用代理IP
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.ip_proxy import IPProxyManager
import requests
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_proxy_usage():
    """
    测试代理IP的使用
    """
    manager = IPProxyManager()
    
    print("开始获取代理IP...")
    
    # 获取一些有效的代理IP
    valid_proxies = manager.get_valid_proxies(count=5, page_range=(1, 2))
    
    if valid_proxies:
        print(f"获取到 {len(valid_proxies)} 个有效代理IP:")
        for i, proxy in enumerate(valid_proxies):
            print(f"{i+1}. {proxy['ip']}:{proxy['port']}")
        
        # 随机获取一个代理使用
        random_proxy = manager.get_random_proxy()
        if random_proxy:
            print(f"\n使用随机代理: {random_proxy['ip']}:{random_proxy['port']}")
            
            # 构造代理字典
            proxy_dict = {
                'http': f"http://{random_proxy['ip']}:{random_proxy['port']}",
                'https': f"http://{random_proxy['ip']}:{random_proxy['port']}"
            }
            
            try:
                # 测试使用代理访问网站
                response = requests.get('http://httpbin.org/ip', proxies=proxy_dict, timeout=10)
                print(f"使用代理访问成功，响应: {response.json()}")
            except Exception as e:
                print(f"使用代理访问失败: {str(e)}")
    else:
        print("未能获取到有效代理IP，请稍后再试")
    
    # 测试刷新代理池
    print("\n刷新代理池...")
    manager.refresh_proxy_pool(count=3)
    print(f"代理池中有 {len(manager.proxy_list)} 个有效代理")

def test_single_page_fetch():
    """
    测试从单页获取代理IP
    """
    manager = IPProxyManager()
    
    print("测试从第一页获取代理IP...")
    proxies = manager.fetch_proxies_from_page(1)
    
    print(f"从第一页获取到 {len(proxies)} 个IP:")
    for i, proxy in enumerate(proxies[:10]):  # 只显示前10个
        print(f"{i+1}. {proxy['ip']}:{proxy['port']}")

if __name__ == "__main__":
    print("=== IP代理模块使用示例 ===\n")
    
    print("1. 测试获取有效代理IP:")
    test_proxy_usage()
    
    print("\n" + "="*50 + "\n")
    
    print("2. 测试从单页获取IP:")
    test_single_page_fetch()
    
    print("\n=== 示例结束 ===")