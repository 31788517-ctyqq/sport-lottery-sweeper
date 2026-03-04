"""
优化版IP代理模块
专注于从预设IP中构建120个IP的代理池
"""

import requests
from bs4 import BeautifulSoup
import re
import random
import time
from typing import List, Dict, Optional
import logging

class OptimizedIPProxyManager:
    """
    优化版IP代理管理器
    专注于使用预设IP构建120个IP的代理池
    """
    
    def __init__(self):
        self.proxy_list = []
        self.logger = logging.getLogger(__name__)
        
        # 预设IP列表（从用户提供的数据中添加）
        self.preset_ips = [
            {'ip': '114.231.42.186', 'port': '8888'},
            {'ip': '114.232.109.160', 'port': '8089'},
            {'ip': '117.69.233.72', 'port': '8089'},
            {'ip': '47.99.131.59', 'port': '80'},
            {'ip': '117.71.133.22', 'port': '8089'},
            {'ip': '183.164.243.67', 'port': '8089'},
            {'ip': '42.63.65.88', 'port': '80'},
            {'ip': '117.86.12.150', 'port': '8089'},
            {'ip': '60.188.5.148', 'port': '80'},
            {'ip': '223.215.176.114', 'port': '8089'},
            {'ip': '60.205.249.70', 'port': '7890'},
            {'ip': '114.103.88.100', 'port': '8089'},
            {'ip': '61.160.202.63', 'port': '80'},
            {'ip': '112.17.16.225', 'port': '80'},
            {'ip': '47.97.16.1', 'port': '80'},
            {'ip': '114.232.110.251', 'port': '8888'},
            {'ip': '114.55.176.241', 'port': '80'},
            {'ip': '113.223.213.40', 'port': '8089'},
            {'ip': '118.178.234.232', 'port': '80'},
            {'ip': '42.63.65.38', 'port': '80'},
            {'ip': '114.231.41.54', 'port': '8888'},
            {'ip': '114.231.42.126', 'port': '8888'},
            {'ip': '117.69.237.65', 'port': '8089'},
            {'ip': '117.69.236.178', 'port': '8089'},
            {'ip': '120.26.160.69', 'port': '80'},
            {'ip': '120.55.74.80', 'port': '80'},
            {'ip': '36.6.144.96', 'port': '8089'},
            {'ip': '113.78.190.20', 'port': '1111'},
            {'ip': '113.223.212.31', 'port': '8089'},
            {'ip': '117.69.236.88', 'port': '8089'},
            {'ip': '182.34.18.25', 'port': '9999'},
            {'ip': '114.235.145.165', 'port': '8089'},
            {'ip': '14.29.108.150', 'port': '8998'},
            {'ip': '120.79.21.48', 'port': '8089'},
            {'ip': '117.71.132.62', 'port': '8089'},
            {'ip': '113.223.215.185', 'port': '8089'},
            {'ip': '117.71.132.113', 'port': '8089'},
            {'ip': '183.164.242.176', 'port': '8089'},
            {'ip': '60.188.5.168', 'port': '80'},
            {'ip': '117.69.236.94', 'port': '8089'},
            # 新增的IP列表
            {'ip': '117.69.237.66', 'port': '8089'},
            {'ip': '49.71.144.207', 'port': '8089'},
            {'ip': '36.6.144.21', 'port': '8089'},
            {'ip': '60.174.0.98', 'port': '8089'},
            {'ip': '47.98.107.25', 'port': '80'},
            {'ip': '117.57.93.128', 'port': '8089'},
            {'ip': '111.225.152.116', 'port': '8089'},
            {'ip': '117.71.149.148', 'port': '8089'},
            {'ip': '117.71.155.199', 'port': '8089'},
            {'ip': '113.121.22.64', 'port': '8089'},
            {'ip': '47.99.71.210', 'port': '80'},
            {'ip': '117.69.236.223', 'port': '8089'},
            {'ip': '118.31.247.119', 'port': '80'},
            {'ip': '117.71.154.42', 'port': '8089'},
            {'ip': '114.231.82.186', 'port': '8089'},
            # 最新添加的IP列表
            {'ip': '36.6.145.95', 'port': '8089'},
            {'ip': '117.69.236.2', 'port': '8089'},
            {'ip': '117.69.233.126', 'port': '8089'},
            {'ip': '183.164.243.44', 'port': '8089'},
            {'ip': '117.69.236.202', 'port': '8089'},
            {'ip': '183.164.242.70', 'port': '8089'},
            {'ip': '117.71.149.111', 'port': '8089'},
            {'ip': '183.164.242.211', 'port': '8089'},
            {'ip': '121.207.92.68', 'port': '8888'},
            {'ip': '114.231.8.15', 'port': '8089'},
            {'ip': '113.223.215.149', 'port': '8089'},
            {'ip': '47.108.59.58', 'port': '7890'},
            {'ip': '114.231.45.165', 'port': '8888'},
            {'ip': '113.121.38.178', 'port': '9999'},
            {'ip': '117.71.149.80', 'port': '8089'},
            {'ip': '114.231.42.114', 'port': '8089'},
            {'ip': '221.130.192.234', 'port': '80'},
            {'ip': '114.231.46.37', 'port': '8089'},
            {'ip': '61.130.9.37', 'port': '443'},
            {'ip': '183.164.242.91', 'port': '8089'},
            {'ip': '117.71.132.95', 'port': '8089'},
            {'ip': '117.71.149.67', 'port': '8089'},
            {'ip': '113.223.215.2', 'port': '8089'},
            {'ip': '121.37.201.60', 'port': '10000'},
            {'ip': '117.71.132.113', 'port': '8089'},
            {'ip': '125.229.149.168', 'port': '65110'},
            {'ip': '61.160.202.107', 'port': '80'},
            {'ip': '117.69.236.209', 'port': '8089'},
            {'ip': '60.188.5.235', 'port': '80'},
            {'ip': '60.174.0.172', 'port': '8089'},
            {'ip': '117.71.155.57', 'port': '8089'},
            {'ip': '101.42.237.144', 'port': '7890'},
            {'ip': '114.232.109.89', 'port': '8089'},
            {'ip': '47.96.252.192', 'port': '80'},
            {'ip': '180.121.131.59', 'port': '8089'},
            {'ip': '111.225.153.136', 'port': '8089'},
            {'ip': '117.69.232.125', 'port': '8089'},
            {'ip': '113.121.42.73', 'port': '9999'},
            {'ip': '117.71.154.154', 'port': '8089'},
            {'ip': '114.231.45.161', 'port': '8888'},
            # 再次添加的IP列表
            {'ip': '223.215.177.1', 'port': '8089'},
            {'ip': '223.215.177.140', 'port': '8089'},
            {'ip': '36.6.144.48', 'port': '8089'},
            {'ip': '36.6.144.82', 'port': '8089'},
            {'ip': '117.57.92.89', 'port': '8089'},
            {'ip': '113.223.212.69', 'port': '8089'},
            {'ip': '114.231.46.48', 'port': '8089'},
            {'ip': '117.69.237.252', 'port': '8089'},
            {'ip': '36.6.144.237', 'port': '8089'},
            {'ip': '116.205.229.85', 'port': '80'},
            {'ip': '47.92.155.21', 'port': '8118'},
            {'ip': '159.226.227.85', 'port': '80'},
            {'ip': '221.224.25.37', 'port': '3128'},
            {'ip': '114.231.42.80', 'port': '8888'},
            {'ip': '60.5.254.20', 'port': '8080'},
            # 最新添加的IP列表
            {'ip': '183.164.243.2', 'port': '8089'},
            {'ip': '117.71.132.247', 'port': '8089'},
            {'ip': '120.77.215.57', 'port': '80'},
            {'ip': '117.69.237.50', 'port': '8089'},
            {'ip': '123.245.249.228', 'port': '8089'},
            {'ip': '112.243.88.8', 'port': '9000'},
            {'ip': '113.121.21.200', 'port': '9999'},
            {'ip': '114.232.109.88', 'port': '8089'},
            {'ip': '47.99.79.60', 'port': '80'},
            {'ip': '120.26.200.226', 'port': '80'},
            {'ip': '114.232.110.142', 'port': '8888'},
            {'ip': '114.232.109.92', 'port': '8089'},
            {'ip': '116.62.34.88', 'port': '80'},
            {'ip': '117.71.132.62', 'port': '8089'},
            {'ip': '114.104.135.72', 'port': '41122'}
        ]
        
        # 初始化时添加预设IP
        self.proxy_list.extend(self.preset_ips)
    
    def _validate_ip(self, ip: str) -> bool:
        """
        验证IP地址格式是否正确
        :param ip: IP地址字符串
        :return: 是否为有效IP
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
    
    def validate_proxy_format(self, proxy: Dict[str, str]) -> bool:
        """
        验证代理IP格式是否正确
        :param proxy: 代理IP信息 {'ip': 'xxx.xxx.xxx.xxx', 'port': 'xxxx'}
        :return: 代理格式是否正确
        """
        return (
            self._validate_ip(proxy['ip']) and 
            proxy['port'].isdigit() and 
            1 <= int(proxy['port']) <= 65535
        )
    
    def refresh_proxy_pool(self, target_count: int = 120):
        """
        刷新代理池，使用预设IP达到目标数量
        :param target_count: 目标IP数量
        """
        # 过滤出格式正确的预设IP
        valid_presets = [ip for ip in self.preset_ips if self.validate_proxy_format(ip)]
        
        # 选取前target_count个有效的预设IP
        selected_ips = valid_presets[:target_count]
        
        # 更新代理池
        self.proxy_list = selected_ips
        
        self.logger.info(f"代理池已刷新，当前有 {len(self.proxy_list)} 个格式正确的代理IP")
    
    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """
        获取一个随机的有效代理IP
        :return: 代理IP信息或None
        """
        if self.proxy_list:
            return random.choice(self.proxy_list)
        return None
    
    def get_proxy_statistics(self) -> Dict[str, int]:
        """
        获取代理池统计信息
        :return: 包含统计信息的字典
        """
        provinces = {}
        operators = {}
        
        # 简单地根据IP段判断归属地
        for proxy in self.proxy_list:
            ip = proxy['ip']
            if ip.startswith('114.'):
                provinces['江苏'] = provinces.get('江苏', 0) + 1
                operators['电信'] = operators.get('电信', 0) + 1
            elif ip.startswith('117.'):
                provinces['安徽'] = provinces.get('安徽', 0) + 1
                operators['电信'] = operators.get('电信', 0) + 1
            elif ip.startswith('183.'):
                provinces['安徽'] = provinces.get('安徽', 0) + 1
                operators['电信'] = operators.get('电信', 0) + 1
            elif ip.startswith('36.'):
                provinces['安徽'] = provinces.get('安徽', 0) + 1
                operators['电信'] = operators.get('电信', 0) + 1
            else:
                provinces['其他'] = provinces.get('其他', 0) + 1
                operators['其他'] = operators.get('其他', 0) + 1
        
        return {
            'total_count': len(self.proxy_list),
            'provinces_distribution': provinces,
            'operators_distribution': operators
        }


def create_120_ip_pool():
    """
    创建包含120个IP的代理池
    """
    print("="*60)
    print("创建包含120个IP的代理池")
    print("使用预设IP，绕过网站反爬虫限制")
    print("="*60)
    
    # 创建优化版IP代理管理器
    manager = OptimizedIPProxyManager()
    
    print(f"可用预设IP数量: {len(manager.preset_ips)}")
    
    # 刷新代理池到120个IP
    manager.refresh_proxy_pool(target_count=120)
    
    print(f"代理池已创建，包含 {len(manager.proxy_list)} 个IP")
    
    if len(manager.proxy_list) >= 120:
        print(f"✓ 成功创建包含 {len(manager.proxy_list)} 个IP的代理池，达到目标数量")
    else:
        print(f"⚠ 仅有 {len(manager.proxy_list)} 个IP，可能预设IP数量不足")
    
    # 显示统计信息
    stats = manager.get_proxy_statistics()
    print(f"\n代理池统计信息:")
    print(f"  总数量: {stats['total_count']}")
    print(f"  地区分布: {stats['provinces_distribution']}")
    print(f"  运营商分布: {stats['operators_distribution']}")
    
    # 显示前10个和后10个IP
    print(f"\n前10个IP:")
    for i, proxy in enumerate(manager.proxy_list[:10]):
        print(f"  {i+1:2d}. {proxy['ip']}:{proxy['port']}")
    
    if len(manager.proxy_list) > 10:
        print(f"\n后10个IP:")
        for i, proxy in enumerate(manager.proxy_list[-10:], start=len(manager.proxy_list)-9):
            print(f"  {i:2d}. {proxy['ip']}:{proxy['port']}")
    
    print(f"\n代理池创建完成!")
    return len(manager.proxy_list)


if __name__ == "__main__":
    count = create_120_ip_pool()
    if count >= 120:
        print(f"\n结果: 成功创建包含 {count} 个IP的代理池，达到目标要求")
    else:
        print(f"\n结果: 创建了包含 {count} 个IP的代理池")