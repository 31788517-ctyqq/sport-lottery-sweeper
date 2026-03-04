"""
IP代理与爬虫系统集成示例
展示如何将IP代理模块与现有的爬虫系统集成
"""

import asyncio
import sys
import os
from typing import Optional, Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.ip_proxy import IPProxyManager
from crawler.ip_proxy_config import IPProxyConfigManager
import requests
import logging

# AI_WORKING: coder1 @2026-01-27 17:36:34 - 创建IP代理与爬虫系统集成示例
class EnhancedCrawlerWithProxy:
    """
    集成IP代理的增强型爬虫类
    """
    
    def __init__(self):
        self.proxy_manager = IPProxyManager()
        self.config_manager = IPProxyConfigManager()
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
        # 应用配置
        crawler_config = self.config_manager.get_enhanced_crawler_config()
        self.use_proxy = crawler_config['use_proxy']
        self.max_retries = crawler_config['max_retries']
        self.timeout = crawler_config['timeout']
        self.headers = crawler_config['headers']
        
        # 更新session的headers
        self.session.headers.update(self.headers)
    
    def get_request_with_proxy(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        使用代理发送GET请求
        :param url: 请求URL
        :param kwargs: 其他请求参数
        :return: 响应对象或None
        """
        # 合并传入的headers
        headers = kwargs.pop('headers', {})
        all_headers = {**self.headers, **headers}
        
        for attempt in range(self.max_retries):
            try:
                proxy = None
                if self.use_proxy:
                    proxy = self.proxy_manager.get_random_proxy()
                    if proxy:
                        proxy_str = f"{proxy['ip']}:{proxy['port']}"
                        proxies = {
                            'http': f'http://{proxy_str}',
                            'https': f'http://{proxy_str}'
                        }
                        self.logger.info(f"使用代理 {proxy_str} 请求 {url}")
                        
                        response = self.session.get(
                            url, 
                            proxies=proxies, 
                            timeout=self.timeout, 
                            headers=all_headers,
                            **kwargs
                        )
                    else:
                        self.logger.warning(f"无法获取有效代理，直接请求 {url}")
                        response = self.session.get(
                            url, 
                            timeout=self.timeout, 
                            headers=all_headers,
                            **kwargs
                        )
                else:
                    response = self.session.get(
                        url, 
                        timeout=self.timeout, 
                        headers=all_headers,
                        **kwargs
                    )
                
                # 检查响应状态
                if response.status_code == 200:
                    return response
                else:
                    self.logger.warning(f"请求 {url} 返回状态码 {response.status_code}，尝试第 {attempt + 1} 次重试")
                    
            except Exception as e:
                self.logger.warning(f"请求 {url} 失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                
                # 如果是最后一次尝试，抛出异常
                if attempt == self.max_retries - 1:
                    raise e
                
                # 更换代理并重试
                if self.use_proxy:
                    self.proxy_manager.refresh_proxy_pool(count=3)
        
        return None
    
    def crawl_89ip(self) -> Dict[str, Any]:
        """
        爬取89ip网站的示例
        :return: 爬取结果
        """
        try:
            # 获取第一页数据
            url = "https://www.89ip.cn/index_1.html"
            response = self.get_request_with_proxy(url)
            
            if response:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 获取页面标题
                title_tag = soup.find('title')
                title = title_tag.get_text() if title_tag else "未找到标题"
                
                # 获取IP地址数量（简单估算）
                ip_count = len(soup.find_all(string=lambda text: text and '.' in text and any(c.isdigit() for c in text)))
                
                return {
                    "success": True,
                    "url": url,
                    "title": title,
                    "estimated_ips": ip_count,
                    "content_length": len(response.text)
                }
            else:
                return {
                    "success": False,
                    "error": "无法获取响应"
                }
        except Exception as e:
            self.logger.error(f"爬取89ip失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_proxy_pool(self, count: int = 10):
        """
        更新代理池
        :param count: 代理数量
        """
        self.proxy_manager.refresh_proxy_pool(count=count)


def run_integration_example():
    """
    运行集成示例
    """
    print("=== IP代理与爬虫系统集成示例 ===\n")
    
    # 创建增强型爬虫实例
    enhanced_crawler = EnhancedCrawlerWithProxy()
    
    print("1. 配置信息:")
    config = enhanced_crawler.config_manager.get_enhanced_crawler_config()
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    print(f"\n2. 预设IP代理信息:")
    print(f"   预设IP总数: {len(enhanced_crawler.proxy_manager.preset_ips)}")
    print("   前5个预设IP:")
    for i, ip in enumerate(enhanced_crawler.proxy_manager.preset_ips[:5]):
        print(f"   {i+1}. {ip['ip']}:{ip['port']}")
    
    print(f"\n3. 当前代理池信息:")
    print(f"   代理池总数: {len(enhanced_crawler.proxy_manager.proxy_list)}")
    
    print("\n4. 验证预设IP可用性 (前5个):")
    valid_count = 0
    for i, proxy in enumerate(enhanced_crawler.proxy_manager.preset_ips[:5]):
        is_valid = enhanced_crawler.proxy_manager.validate_proxy(proxy)
        status = "✓ 可用" if is_valid else "✗ 不可用"
        print(f"   {i+1}. {proxy['ip']}:{proxy['port']} - {status}")
        if is_valid:
            valid_count += 1
    
    print(f"\n   验证结果: {valid_count}/5 个预设IP可用")
    
    print("\n5. 使用代理爬取示例:")
    result = enhanced_crawler.crawl_89ip()
    print(f"   爬取结果: {result}")
    
    print("\n6. 测试代理请求:")
    try:
        # 尝试使用代理访问一个公开的IP检测服务
        test_url = "http://httpbin.org/ip"
        response = enhanced_crawler.get_request_with_proxy(test_url)
        if response:
            import json
            ip_info = response.json()
            print(f"   通过代理访问 {test_url} 成功，返回IP信息: {ip_info}")
        else:
            print("   通过代理访问失败")
    except Exception as e:
        print(f"   通过代理访问出错: {str(e)}")
    
    print("\n=== 集成示例结束 ===")


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    run_integration_example()

# AI_DONE: coder1 @2026-01-27 17:36:34