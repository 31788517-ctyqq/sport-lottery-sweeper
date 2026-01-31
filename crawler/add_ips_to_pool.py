"""
IP代理池添加器
将提供的IP列表添加到IP代理池中
"""

import re
from typing import List, Dict
from crawler.ip_proxy import IPProxyManager
from backend.scrapers.core.proxy_pool import ProxyPool
import asyncio


def parse_ip_list(ip_text: str) -> List[Dict[str, str]]:
    """
    解析IP列表文本，提取IP和端口信息
    """
    lines = ip_text.strip().split('\n')
    ips = []
    
    # 跳过标题行，从第二行开始解析
    for line in lines[1:]:
        parts = line.split('\t')
        if len(parts) >= 5:  # 确保有足够的字段
            ip = parts[0].strip()
            port = parts[1].strip()
            
            # 验证IP格式
            if is_valid_ip(ip):
                ips.append({
                    'ip': ip,
                    'port': port,
                    'location': parts[2].strip(),
                    'provider': parts[3].strip(),
                    'time': parts[4].strip()
                })
    
    return ips


def is_valid_ip(ip: str) -> bool:
    """
    验证IP地址格式是否正确
    """
    pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    match = re.match(pattern, ip)
    if match:
        # 验证每个数字是否在0-255范围内
        for num in match.groups():
            if int(num) > 255:
                return False
        return True
    return False


def create_proxy_urls(ips: List[Dict[str, str]]) -> List[str]:
    """
    将IP信息转换为代理URL格式
    """
    proxy_urls = []
    for ip_info in ips:
        proxy_url = f"http://{ip_info['ip']}:{ip_info['port']}"
        proxy_urls.append(proxy_url)
    
    return proxy_urls


async def add_ips_to_existing_pool(ips: List[Dict[str, str]]):
    """
    将IP添加到现有的代理池中
    """
    # 创建代理URL列表
    proxy_urls = create_proxy_urls(ips)
    
    # 获取全局代理池实例
    proxy_pool = await get_proxy_pool_from_backend()
    
    # 添加代理到池中
    added_count = 0
    for url in proxy_urls:
        if proxy_pool.add_proxy(url):
            added_count += 1
    
    print(f"成功添加 {added_count}/{len(proxy_urls)} 个代理到代理池")
    
    return proxy_pool


async def get_proxy_pool_from_backend():
    """
    从后端获取代理池实例
    """
    # 由于backend的proxy_pool是异步的，我们需要创建一个新的实例
    from backend.scrapers.core.proxy_pool import ProxyPool
    # 使用一个简单的测试URL
    proxy_pool = ProxyPool(
        test_url="http://httpbin.org/ip",
        test_timeout=10
    )
    return proxy_pool


def add_ips_to_ip_proxy_manager(ips: List[Dict[str, str]]):
    """
    将IP添加到IPProxyManager中
    """
    manager = IPProxyManager()
    
    # 将IP添加到内部列表中
    for ip_info in ips:
        proxy = {
            'ip': ip_info['ip'],
            'port': ip_info['port']
        }
        # 添加到内部列表，以便后续验证和使用
        if proxy not in manager.proxy_list:
            manager.proxy_list.append(proxy)
    
    print(f"已将 {len(ips)} 个IP添加到IP代理管理器")
    return manager


def main():
    # 提供的IP列表
    ip_text = """IP	端口号	代理位置	运营商	录取时间
114.231.42.186	8888	江苏省南通市	电信	2026/01/27 17:30:02
114.232.109.160	8089	江苏省南通市	电信	2026/01/27 17:30:02
117.69.233.72	8089	安徽省淮北市	电信	2026/01/27 17:30:02
47.99.131.59	80	浙江省杭州市	阿里云	2026/01/27 17:30:02
117.71.133.22	8089	安徽省铜陵市	电信	2026/01/27 17:30:02
183.164.243.67	8089	安徽省淮北市	电信	2026/01/27 17:30:02
42.63.65.88	80	宁夏	联通	2026/01/27 17:30:02
117.86.12.150	8089	江苏省南通市	电信	2026/01/27 17:30:02
60.188.5.148	80	浙江省台州市黄岩区	电信	2026/01/27 17:30:02
223.215.176.114	8089	安徽省马鞍山市	电信	2026/01/27 17:30:02
60.205.249.70	7890	北京市	阿里云BGP服务器	2026/01/27 17:30:02
114.103.88.100	8089	安徽省滁州市	电信	2026/01/27 17:30:02
61.160.202.63	80	江苏省常州市	电信	2026/01/27 17:30:02
112.17.16.225	80	浙江省杭州市	移动	2026/01/27 17:30:02
47.97.16.1	80	浙江省杭州市	阿里云	2026/01/27 17:30:02
114.232.110.251	8888	江苏省南通市	电信	2026/01/27 17:30:02
114.55.176.241	80	浙江省杭州市	阿里云BGP数据中心	2026/01/27 17:30:02
113.223.213.40	8089	湖南省衡阳市	电信	2026/01/27 17:30:02
118.178.234.232	80	浙江省杭州市	阿里云计算有限公司	2026/01/27 17:30:02
42.63.65.38	80	宁夏	联通	2026/01/27 17:30:02
114.231.41.54	8888	江苏省南通市	电信	2026/01/27 17:30:02
114.231.42.126	8888	江苏省南通市	电信	2026/01/27 17:30:02
117.69.237.65	8089	安徽省淮北市	电信	2026/01/27 17:30:02
117.69.236.178	8089	安徽省淮北市	电信	2026/01/27 17:30:02
120.26.160.69	80	浙江省杭州市	阿里巴巴网络有限公司BGP数据中心(BGP)	2026/01/27 17:30:02
120.55.74.80	80	浙江省杭州市	阿里云BGP数据中心	2026/01/27 17:30:02
36.6.144.96	8089	安徽省亳州市	电信	2026/01/27 17:30:02
113.78.190.20	1111	广东省东莞市	电信	2026/01/27 17:30:02
113.223.212.31	8089	湖南省衡阳市	电信	2026/01/27 17:30:02
117.69.236.88	8089	安徽省淮北市	电信	2026/01/27 17:30:02
182.34.18.25	9999	山东省烟台市	电信	2026/01/27 17:30:02
114.235.145.165	8089	江苏省徐州市	电信	2026/01/27 17:30:02
14.29.108.150	8998	广东省广州市	电信	2026/01/27 17:30:02
120.79.21.48	8089	浙江省杭州市	阿里云BGP数据中心	2026/01/27 17:30:02
117.71.132.62	8089	安徽省铜陵市	电信	2026/01/27 17:30:02
113.223.215.185	8089	湖南省衡阳市	电信	2026/01/27 17:30:02
117.71.132.113	8089	安徽省铜陵市	电信	2026/01/27 17:30:02
183.164.242.176	8089	安徽省淮北市	电信	2026/01/27 17:30:02
60.188.5.168	80	浙江省台州市黄岩区	电信	2026/01/27 17:30:02
117.69.236.94	8089	安徽省淮北市	电信	2026/01/27 17:30:02"""
    
    # 解析IP列表
    ips = parse_ip_list(ip_text)
    print(f"解析到 {len(ips)} 个IP地址")
    
    # 将IP添加到IPProxyManager
    manager = add_ips_to_ip_proxy_manager(ips)
    
    # 输出前几个IP作为验证
    print("\n添加的前5个IP:")
    for i, proxy in enumerate(manager.proxy_list[:5]):
        print(f"  {i+1}. {proxy['ip']}:{proxy['port']}")
    
    if len(manager.proxy_list) > 5:
        print(f"  ... 还有 {len(manager.proxy_list) - 5} 个IP")
    
    # 异步部分：添加到后端代理池
    print("\n正在添加到后端代理池...")
    asyncio.run(add_ips_to_existing_pool(ips))


if __name__ == "__main__":
    main()