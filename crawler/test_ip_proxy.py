"""
IP代理模块测试脚本
用于测试IPProxyManager类的基本功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.ip_proxy import IPProxyManager
import unittest
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TestIPProxyManager(unittest.TestCase):
    """IP代理管理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = IPProxyManager()
    
    def test_validate_ip(self):
        """测试IP地址验证功能"""
        # 有效的IP地址
        self.assertTrue(self.manager._validate_ip("192.168.1.1"))
        self.assertTrue(self.manager._validate_ip("8.8.8.8"))
        self.assertTrue(self.manager._validate_ip("127.0.0.1"))
        
        # 无效的IP地址
        self.assertFalse(self.manager._validate_ip("256.1.1.1"))  # 数字超过255
        self.assertFalse(self.manager._validate_ip("192.168.1"))   # 缺少一部分
        self.assertFalse(self.manager._validate_ip("192.168.1.1.1"))  # 多了一部分
        self.assertFalse(self.manager._validate_ip("abc.def.ghi.jkl"))  # 非数字
        self.assertFalse(self.manager._validate_ip(""))  # 空字符串
    
    def test_fetch_proxies_from_page(self):
        """测试从页面获取代理IP"""
        # 由于网络请求可能不稳定，这里只测试基本功能
        # 不验证返回的具体内容，只验证不抛出异常
        try:
            proxies = self.manager.fetch_proxies_from_page(1)
            # 可能返回空列表，这在代理网站不稳定时是正常的
            self.assertIsInstance(proxies, list)
        except Exception as e:
            # 网络请求失败是正常的，只需记录
            logging.warning(f"获取代理IP失败: {str(e)}")
    
    def test_get_random_proxy(self):
        """测试获取随机代理功能"""
        # 这个测试可能因为网络问题而失败，所以用try-catch包围
        try:
            proxy = self.manager.get_random_proxy()
            # 可能返回None，这在没有有效代理时是正常的
            if proxy is not None:
                self.assertIn('ip', proxy)
                self.assertIn('port', proxy)
        except Exception as e:
            logging.warning(f"获取随机代理失败: {str(e)}")
    
    def test_proxy_format(self):
        """测试代理格式"""
        # 测试几个已知的代理格式
        test_proxies = [
            {'ip': '192.168.1.1', 'port': '8080'},
            {'ip': '8.8.8.8', 'port': '3128'}
        ]
        
        for proxy in test_proxies:
            self.assertIn('ip', proxy)
            self.assertIn('port', proxy)
            self.assertTrue(self.manager._validate_ip(proxy['ip']))
            self.assertTrue(proxy['port'].isdigit())

def run_basic_tests():
    """运行基本测试"""
    print("运行IP代理模块基本测试...")
    
    # 创建测试实例
    manager = IPProxyManager()
    
    # 测试IP验证功能
    print("1. 测试IP验证功能:")
    print(f"   192.168.1.1 -> {manager._validate_ip('192.168.1.1')} (应为True)")
    print(f"   256.1.1.1 -> {manager._validate_ip('256.1.1.1')} (应为False)")
    
    # 测试获取代理（基本功能）
    print("\n2. 测试获取代理功能:")
    try:
        proxies = manager.fetch_proxies_from_page(1)
        print(f"   从第一页获取到 {len(proxies)} 个代理")
        for i, proxy in enumerate(proxies[:3]):  # 显示前3个
            print(f"   {i+1}. {proxy['ip']}:{proxy['port']}")
    except Exception as e:
        print(f"   获取代理时出错: {str(e)}")
    
    print("\n基本测试完成!")

if __name__ == "__main__":
    print("=== IP代理模块测试 ===\n")
    
    # 运行基本测试
    run_basic_tests()
    
    print("\n" + "="*50)
    print("是否运行完整单元测试？(y/n): ", end="")
    choice = input().lower()
    
    if choice == 'y' or choice == 'yes':
        print("\n运行单元测试:")
        unittest.main(argv=[''], exit=False, verbosity=2)