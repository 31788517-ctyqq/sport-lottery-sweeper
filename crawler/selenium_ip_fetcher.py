"""
使用Selenium绕过CloudFlare保护来获取89ip.cn的IP
"""
import time
import random
import re
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SeleniumIPFetcher:
    """
    使用Selenium绕过CloudFlare保护的IP获取器
    """
    
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """
        设置Chrome驱动
        """
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 随机User-Agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            # 执行脚本隐藏webdriver特征
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            logger.error(f"初始化Chrome驱动失败: {e}")
            raise
    
    def fetch_proxies_from_page(self, page_num: int = 1) -> List[Dict[str, str]]:
        """
        从指定页面获取代理IP列表
        :param page_num: 页码
        :return: 代理IP列表
        """
        url = f"https://www.89ip.cn/index_{page_num}.html"
        
        try:
            logger.info(f"正在访问 {url}")
            self.driver.get(url)
            
            # 等待页面加载，可能需要处理CloudFlare防护
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 检查是否遇到CloudFlare防护页面
            title = self.driver.title.lower()
            if "cloudflare" in title or "just a moment" in title or "checking your browser" in title:
                logger.info("检测到CloudFlare防护，等待验证...")
                # 等待更长时间让CloudFlare验证通过
                time.sleep(10)
            
            # 等待内容加载
            time.sleep(3)
            
            # 获取页面源码
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 解析IP和端口
            ip_port_list = []
            
            # 查找表格行
            table_rows = soup.select('table tr')
            
            for row in table_rows:
                tds = row.find_all('td')
                if len(tds) >= 2:
                    ip_text = tds[0].get_text(strip=True)
                    port_text = tds[1].get_text(strip=True)
                    
                    # 验证IP格式
                    if self._validate_ip(ip_text) and port_text.isdigit():
                        ip_port_list.append({
                            'ip': ip_text,
                            'port': port_text
                        })
            
            # 如果表格中没有找到，尝试其他方式
            if not ip_port_list:
                # 使用正则表达式查找IP:端口模式
                ip_port_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{2,5})'
                matches = re.findall(ip_port_pattern, page_source)
                for ip, port in matches:
                    if self._validate_ip(ip) and 1 <= int(port) <= 65535:
                        ip_port_list.append({
                            'ip': ip,
                            'port': port
                        })
            
            # 去重
            unique_proxies = []
            seen = set()
            for proxy in ip_port_list:
                key = (proxy['ip'], proxy['port'])
                if key not in seen:
                    seen.add(key)
                    unique_proxies.append(proxy)
            
            logger.info(f"从第 {page_num} 页获取到 {len(unique_proxies)} 个代理IP")
            return unique_proxies
            
        except Exception as e:
            logger.error(f"从第 {page_num} 页获取代理IP时出错: {e}")
            return []
    
    def _validate_ip(self, ip: str) -> bool:
        """
        验证IP地址格式是否正确
        """
        pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
        match = re.match(pattern, ip)
        if match:
            for num in match.groups():
                if int(num) > 255:
                    return False
            return True
        return False
    
    def fetch_multiple_pages(self, start_page: int = 1, end_page: int = 3) -> List[Dict[str, str]]:
        """
        获取多个页面的代理IP
        """
        all_proxies = []
        for page in range(start_page, end_page + 1):
            logger.info(f"正在获取第 {page} 页...")
            proxies = self.fetch_proxies_from_page(page)
            all_proxies.extend(proxies)
            
            # 添加随机延时
            time.sleep(random.uniform(2, 5))
        
        return all_proxies
    
    def close(self):
        """
        关闭浏览器驱动
        """
        if self.driver:
            self.driver.quit()


def test_selenium_fetcher():
    """
    测试Selenium IP获取器
    """
    try:
        fetcher = SeleniumIPFetcher()
        
        print("开始使用Selenium获取IP...")
        proxies = fetcher.fetch_multiple_pages(1, 3)
        
        print(f"共获取到 {len(proxies)} 个IP:")
        for i, proxy in enumerate(proxies[:30]):  # 显示前30个
            print(f"{i+1:2d}. {proxy['ip']}:{proxy['port']}")
        
        if len(proxies) >= 30:
            print(f"✓ 成功获取 {len(proxies)} 个IP，达到目标数量30个")
        else:
            print(f"⚠ 只获取到 {len(proxies)} 个IP，少于目标数量30个")
        
        fetcher.close()
        
    except ImportError:
        print("Selenium未安装，无法使用浏览器自动化绕过CloudFlare保护")
        print("请运行: pip install selenium beautifulsoup4")
        print("并确保已安装Chrome浏览器和对应的ChromeDriver")
    
    except Exception as e:
        print(f"Selenium获取IP时出错: {e}")


if __name__ == "__main__":
    test_selenium_fetcher()