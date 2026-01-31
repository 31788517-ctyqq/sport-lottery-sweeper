"""
实用爬虫示例
展示如何在实际爬虫中使用动态IP池
"""
import requests
import time
import random
from typing import Optional
import logging

from .ip_proxy import IPProxyManager


class PracticalCrawler:
    """
    实用爬虫类
    演示如何在实际爬虫中使用动态IP池
    """
    
    def __init__(self):
        self.ip_proxy_manager = IPProxyManager()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.logger = logging.getLogger(__name__)
    
    def get_with_proxy(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """
        使用代理获取网页内容
        :param url: 目标URL
        :param max_retries: 最大重试次数
        :return: Response对象或None
        """
        for attempt in range(max_retries):
            # 获取一个随机代理
            proxy = self.ip_proxy_manager.get_random_proxy()
            
            if not proxy:
                self.logger.warning(f"没有可用的代理，尝试刷新代理池")
                self.ip_proxy_manager.refresh_proxy_pool(count=10)
                proxy = self.ip_proxy_manager.get_random_proxy()
                
                if not proxy:
                    self.logger.error("仍然没有可用的代理，放弃请求")
                    return None
            
            proxy_str = f"http://{proxy['ip']}:{proxy['port']}"
            proxies = {
                'http': proxy_str,
                'https': proxy_str
            }
            
            try:
                self.logger.info(f"尝试使用代理 {proxy_str} 访问 {url}")
                
                response = self.session.get(url, proxies=proxies, timeout=10)
                
                if response.status_code == 200:
                    self.logger.info(f"请求成功，使用代理: {proxy_str}")
                    return response
                else:
                    self.logger.warning(f"请求失败，状态码: {response.status_code}，使用代理: {proxy_str}")
                    
            except Exception as e:
                self.logger.warning(f"请求失败: {str(e)}，使用代理: {proxy_str}")
            
            # 短暂休眠，避免请求过于频繁
            time.sleep(random.uniform(1, 2))
        
        self.logger.error(f"经过 {max_retries} 次尝试后仍无法成功访问 {url}")
        return None
    
    def crawl_multiple_urls(self, urls: list) -> list:
        """
        批量爬取多个URL
        :param urls: URL列表
        :return: 成功爬取的响应列表
        """
        results = []
        
        for i, url in enumerate(urls):
            self.logger.info(f"正在爬取 ({i+1}/{len(urls)}): {url}")
            
            response = self.get_with_proxy(url)
            if response:
                results.append({
                    'url': url,
                    'status_code': response.status_code,
                    'content_length': len(response.text),
                    'content': response.text
                })
            
            # 在请求之间添加随机延时，模拟人类行为
            if i < len(urls) - 1:  # 不在最后一个请求后延时
                delay = random.uniform(2, 5)
                self.logger.info(f"等待 {delay:.2f} 秒后继续...")
                time.sleep(delay)
        
        return results


if __name__ == "__main__":
    # 创建爬虫实例
    crawler = PracticalCrawler()
    
    # 示例URL列表（使用一些公开API作为示例）
    test_urls = [
        "http://httpbin.org/ip",  # 返回请求的IP信息
        "https://httpbin.org/user-agent",  # 返回User-Agent
        "https://httpbin.org/headers",  # 返回请求头
    ]
    
    print("开始批量爬取...")
    results = crawler.crawl_multiple_urls(test_urls)
    
    print(f"\n完成爬取，成功获取 {len(results)} 个响应")
    
    for result in results:
        print(f"URL: {result['url']}")
        print(f"状态码: {result['status_code']}")
        print(f"内容长度: {result['content_length']}")
        print("---")
    
    # 显示代理池统计信息
    stats = crawler.ip_proxy_manager.get_proxy_statistics()
    print(f"\n代理池统计信息:")
    print(f"总数量: {stats['total_count']}")
    print(f"地区分布: {stats['provinces_distribution']}")
    print(f"运营商分布: {stats['operators_distribution']}")