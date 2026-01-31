"""
89ip.cn IP获取器
用于从89ip.cn网站获取免费代理IP
"""
import requests
import re
import time
import random
from bs4 import BeautifulSoup
from typing import List, Tuple, Optional
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Ip89Fetcher:
    """89ip.cn IP获取器"""
    
    def __init__(self):
        self.base_url = "https://www.89ip.cn"
        self.session = requests.Session()
        # 使用更真实的请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
    
    def fetch_page(self, page_num: int = 1) -> Optional[BeautifulSoup]:
        """
        获取指定页码的IP列表页面
        :param page_num: 页码，默认为1
        :return: BeautifulSoup对象或None
        """
        try:
            url = f"{self.base_url}/index_{page_num}.html" if page_num > 1 else f"{self.base_url}/index.html"
            logger.info(f"正在获取页面: {url}")
            
            # 添加延时以模拟人类行为
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(url, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                return soup
            else:
                logger.error(f"获取页面失败，状态码: {response.status_code}")
                # 尝试使用会话和cookies
                # 设置一些常见的浏览器属性来绕过检测
                self.session.headers.update({
                    'Referer': 'https://www.google.com/',
                })
                
                # 再次尝试请求
                response = self.session.get(url, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    return soup
                else:
                    logger.error(f"再次获取页面失败，状态码: {response.status_code}")
                    return None
        except requests.exceptions.RequestException as e:
            logger.error(f"请求页面时发生错误: {str(e)}")
            # 尝试使用代理
            return self._fetch_with_proxy(url)
        except Exception as e:
            logger.error(f"获取页面时发生未知错误: {str(e)}")
            return None
    
    def _fetch_with_proxy(self, url: str) -> Optional[BeautifulSoup]:
        """
        使用代理获取页面
        :param url: URL地址
        :return: BeautifulSoup对象或None
        """
        try:
            # 使用公共代理获取页面
            proxies = {
                'http': 'http://127.0.0.1:8080',  # 可以替换为真实可用的代理
                'https': 'http://127.0.0.1:8080'
            }
            
            # 使用不同的请求头
            temp_headers = self.session.headers.copy()
            temp_headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
            })
            
            response = requests.get(url, headers=temp_headers, timeout=15, proxies=None)  # 暂时不用代理测试
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                return soup
        except Exception as e:
            logger.error(f"使用代理获取页面也失败: {str(e)}")
        
        return None
    
    def parse_ip_list(self, soup: BeautifulSoup) -> List[Tuple[str, str]]:
        """
        从页面解析IP和端口
        :param soup: BeautifulSoup对象
        :return: IP和端口的元组列表
        """
        ip_list = []
        
        try:
            # 方法1: 查找包含IP的表格行
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')[1:]  # 跳过标题行
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        ip = cols[0].get_text(strip=True)
                        port = cols[1].get_text(strip=True)
                        
                        # 验证IP格式
                        if self.is_valid_ip(ip) and self.is_valid_port(port):
                            ip_list.append((ip, port))
            
            # 如果方法1没有找到，则尝试其他方法
            if not ip_list:
                # 方法2: 查找所有包含IP格式的文本
                ip_port_patterns = soup.find_all(text=re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*?\d{2,5}'))
                for text in ip_port_patterns:
                    # 使用正则表达式提取IP和端口
                    matches = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*?(\d{2,5})', str(text))
                    for ip, port in matches:
                        if self.is_valid_ip(ip) and self.is_valid_port(port):
                            ip_list.append((ip, port))
            
            # 如果还没有找到，则尝试查找所有文本节点
            if not ip_list:
                # 方法3: 搜索页面中的所有文本
                all_text = soup.get_text()
                matches = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*?(\d{2,5})', all_text)
                for ip, port in matches:
                    if self.is_valid_ip(ip) and self.is_valid_port(port):
                        ip_list.append((ip, port))
                            
        except Exception as e:
            logger.error(f"解析IP列表时发生错误: {str(e)}")
        
        # 去重
        unique_ips = list(set(ip_list))
        logger.info(f"从页面解析到 {len(unique_ips)} 个唯一IP地址")
        return unique_ips
    
    def is_valid_ip(self, ip: str) -> bool:
        """
        验证IP地址格式
        :param ip: IP地址字符串
        :return: 是否为有效IP
        """
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(pattern, ip):
            parts = ip.split('.')
            return all(0 <= int(part) <= 255 for part in parts)
        return False
    
    def is_valid_port(self, port: str) -> bool:
        """
        验证端口号
        :param port: 端口号字符串
        :return: 是否为有效端口
        """
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except ValueError:
            return False
    
    def fetch_ips(self, pages: int = 3) -> List[Tuple[str, str]]:
        """
        获取多个页面的IP地址
        :param pages: 获取页面数量，默认为3
        :return: IP和端口的元组列表
        """
        all_ips = []
        
        for page_num in range(1, pages + 1):
            logger.info(f"正在获取第 {page_num} 页IP...")
            
            soup = self.fetch_page(page_num)
            if soup:
                ips = self.parse_ip_list(soup)
                all_ips.extend(ips)
                
                # 随机延时，避免请求过于频繁
                time.sleep(random.uniform(2, 5))
            else:
                logger.warning(f"获取第 {page_num} 页失败")
                
                # 如果是521错误（Cloudflare），等待更长时间再试
                time.sleep(10)
        
        logger.info(f"总共获取到 {len(all_ips)} 个IP地址")
        return all_ips
    
    def validate_ip_port(self, ip: str, port: str, timeout: int = 5) -> bool:
        """
        验证IP和端口是否可用
        :param ip: IP地址
        :param port: 端口号
        :param timeout: 超时时间
        :return: 是否可用
        """
        try:
            proxy = f"http://{ip}:{port}"
            proxies = {
                "http": proxy,
                "https": proxy
            }
            
            response = requests.get(
                "http://httpbin.org/ip", 
                proxies=proxies, 
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; ProxyValidator/1.0)'
                }
            )
            
            return response.status_code == 200
        except Exception:
            return False


def add_ips_from_89ip_to_pool(ip_pool, pages: int = 3, validate: bool = True) -> int:
    """
    从89ip.cn获取IP并添加到IP池中
    :param ip_pool: IP池对象
    :param pages: 获取页面数量
    :param validate: 是否验证IP可用性
    :return: 成功添加的IP数量
    """
    fetcher = Ip89Fetcher()
    logger.info("开始从89ip.cn获取IP地址...")
    
    ips = fetcher.fetch_ips(pages)
    added_count = 0
    
    for ip, port in ips:
        if validate:
            logger.info(f"正在验证IP: {ip}:{port}")
            if fetcher.validate_ip_port(ip, port):
                logger.info(f"IP验证成功: {ip}:{port}")
                if ip_pool.add_proxy(ip, int(port)):
                    added_count += 1
            else:
                logger.info(f"IP验证失败: {ip}:{port}")
        else:
            if ip_pool.add_proxy(ip, int(port)):
                added_count += 1
    
    logger.info(f"成功从89ip.cn添加了 {added_count} 个IP到IP池")
    return added_count


def demo_89ip_fetcher():
    """演示89ip获取器"""
    print("="*60)
    print("演示: 89ip.cn IP获取器")
    print("="*60)
    
    fetcher = Ip89Fetcher()
    
    # 获取前2页的IP
    ips = fetcher.fetch_ips(pages=2)
    
    print(f"获取到 {len(ips)} 个IP地址:")
    for i, (ip, port) in enumerate(ips[:10]):  # 只显示前10个
        print(f"  {i+1}. {ip}:{port}")
    
    if len(ips) > 10:
        print(f"  ... 还有 {len(ips)-10} 个IP")
    
    print("\n演示完成")


if __name__ == "__main__":
    demo_89ip_fetcher()