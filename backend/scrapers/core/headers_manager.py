"""
请求头伪装和Cookie管理模块
支持动态Header生成、Cookie池管理、指纹伪造
"""
import asyncio
import logging
import random
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import base64
import hashlib
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)


@dataclass
class HeaderProfile:
    """请求头配置文件"""
    name: str
    base_headers: Dict[str, str]
    user_agents: List[str]
    referer_templates: List[str]
    accept_languages: List[str]
    platforms: List[str]  # desktop, mobile, tablet
    
    def generate_headers(self, platform: str = "desktop") -> Dict[str, str]:
        """生成请求头"""
        headers = self.base_headers.copy()
        
        # 随机选择User-Agent
        headers['User-Agent'] = random.choice(self.user_agents)
        
        # 随机选择Accept-Language
        if self.accept_languages:
            headers['Accept-Language'] = random.choice(self.accept_languages)
        
        # 生成随机Referer
        if self.referer_templates:
            template = random.choice(self.referer_templates)
            headers['Referer'] = template.format(
                timestamp=int(time.time()),
                random_id=random.randint(1000, 9999)
            )
        
        # 平台特定头部
        if platform == "mobile":
            headers['Sec-CH-UA-Mobile'] = '?1'
            headers['Sec-CH-UA-Platform'] = '"Android"'
        elif platform == "tablet":
            headers['Sec-CH-UA-Mobile'] = '?0'
            headers['Sec-CH-UA-Platform'] = '"macOS"'
        
        # 添加一些随机的安全头部
        if random.random() > 0.5:
            headers['Sec-Fetch-Dest'] = random.choice(['document', 'empty', 'image'])
            headers['Sec-Fetch-Mode'] = random.choice(['navigate', 'cors', 'no-cors'])
            headers['Sec-Fetch-Site'] = random.choice(['same-origin', 'same-site', 'cross-site'])
        
        return headers


@dataclass
class Cookie:
    """Cookie信息"""
    name: str
    value: str
    domain: str
    path: str = "/"
    expires: Optional[datetime] = None
    secure: bool = False
    http_only: bool = False
    same_site: str = "Lax"


class CookieManager:
    """Cookie管理器"""
    
    def __init__(self, cookie_file: str = None):
        """
        初始化Cookie管理器
        
        Args:
            cookie_file: Cookie存储文件路径
        """
        self.cookies: Dict[str, List[Cookie]] = {}  # domain -> cookies
        self.cookie_file = cookie_file
        self.session_cookies: Dict[str, str] = {}  # 当前会话的cookies
        
        if cookie_file:
            self.load_cookies()
    
    def add_cookie(self, cookie: Cookie):
        """添加Cookie"""
        domain = cookie.domain.lower()
        if domain not in self.cookies:
            self.cookies[domain] = []
        
        # 检查是否已存在同名cookie
        for i, existing in enumerate(self.cookies[domain]):
            if existing.name == cookie.name:
                self.cookies[domain][i] = cookie
                return
        
        self.cookies[domain].append(cookie)
        logger.debug(f"添加Cookie: {cookie.name}={cookie.value[:10]}... for {domain}")
    
    def get_cookies_for_domain(self, domain: str) -> Dict[str, str]:
        """获取指定域名的Cookies"""
        domain = domain.lower()
        cookies = {}
        
        # 从持久化存储获取
        if domain in self.cookies:
            now = datetime.now()
            for cookie in self.cookies[domain]:
                if not cookie.expires or cookie.expires > now:
                    cookies[cookie.name] = cookie.value
        
        # 合并会话cookies
        for name, value in self.session_cookies.items():
            if domain in name.lower() or any(domain.endswith(d) for d in self.cookies.keys()):
                cookies[name] = value
        
        return cookies
    
    def update_from_response(self, url: str, response_headers: Dict[str, str]):
        """从响应头更新Cookies"""
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        domain = parsed.netloc
        
        set_cookie_headers = response_headers.get('set-cookie', [])
        if isinstance(set_cookie_headers, str):
            set_cookie_headers = [set_cookie_headers]
        
        for set_cookie in set_cookie_headers:
            cookie = self._parse_set_cookie_header(set_cookie, domain)
            if cookie:
                self.add_cookie(cookie)
                # 添加到会话cookies
                self.session_cookies[cookie.name] = cookie.value
    
    def _parse_set_cookie_header(self, set_cookie: str, default_domain: str) -> Optional[Cookie]:
        """解析Set-Cookie头部"""
        try:
            parts = set_cookie.split(';')
            name_value = parts[0].strip().split('=', 1)
            
            if len(name_value) != 2:
                return None
            
            name, value = name_value
            
            # 默认值
            cookie = Cookie(
                name=name.strip(),
                value=value.strip(),
                domain=default_domain
            )
            
            # 解析属性
            for part in parts[1:]:
                attr_parts = part.strip().split('=', 1)
                attr_name = attr_parts[0].strip().lower()
                attr_value = attr_parts[1].strip() if len(attr_parts) > 1 else None
                
                if attr_name == 'domain':
                    cookie.domain = attr_value
                elif attr_name == 'path':
                    cookie.path = attr_value
                elif attr_name == 'expires':
                    try:
                        cookie.expires = datetime.strptime(attr_value, '%a, %d %b %Y %H:%M:%S GMT')
                    except ValueError:
                        pass
                elif attr_name == 'max-age':
                    try:
                        max_age = int(attr_value)
                        cookie.expires = datetime.now() + timedelta(seconds=max_age)
                    except ValueError:
                        pass
                elif attr_name == 'secure':
                    cookie.secure = True
                elif attr_name == 'httponly':
                    cookie.http_only = True
                elif attr_name == 'samesite':
                    cookie.same_site = attr_value
            
            return cookie
            
        except Exception as e:
            logger.warning(f"解析Set-Cookie失败: {set_cookie}, 错误: {e}")
            return None
    
    def generate_browser_fingerprint(self) -> Dict[str, str]:
        """生成浏览器指纹"""
        # Canvas指纹 (简化版)
        canvas_fp = hashlib.md5(str(random.random()).encode()).hexdigest()[:16]
        
        # WebGL指纹
        webgl_fp = hashlib.md5(str(time.time() + random.random()).encode()).hexdigest()[:16]
        
        # 屏幕分辨率
        resolutions = [
            '1920x1080', '1366x768', '1440x900', '1536x864',
            '2560x1440', '1280x720', '1600x900', '2048x1152'
        ]
        screen_res = random.choice(resolutions)
        
        # 时区
        timezones = ['Asia/Shanghai', 'Asia/Beijing', 'UTC+8', 'GMT+0800']
        timezone = random.choice(timezones)
        
        # 语言
        languages = ['zh-CN', 'zh', 'en-US', 'en']
        language = random.choice(languages)
        
        return {
            'canvas_fp': canvas_fp,
            'webgl_fp': webgl_fp,
            'screen_res': screen_res,
            'timezone': timezone,
            'language': language,
            'platform': random.choice(['Win32', 'MacIntel', 'Linux x86_64']),
            'hardware_concurrency': str(random.choice([2, 4, 6, 8, 12, 16])),
            'device_memory': str(random.choice([4, 8, 16, 32]))
        }
    
    def get_headers_with_fingerprint(self, base_headers: Dict[str, str] = None) -> Dict[str, str]:
        """获取包含指纹的请求头"""
        headers = base_headers.copy() if base_headers else {}
        
        # 添加指纹相关头部
        fp = self.generate_browser_fingerlogger.debug()
        
        # Sec-CH-UA (Chrome的用户代理客户端提示)
        chrome_versions = ['91', '92', '93', '94', '95', '96', '97', '98', '99', '100']
        headers['sec-ch-ua'] = f'" Not A;Brand";v="99", "Chromium";v="{random.choice(chrome_versions)}", "Google Chrome";v="{random.choice(chrome_versions)}"'
        
        # Sec-CH-UA-Platform
        headers['sec-ch-ua-platform'] = f'"{fp["platform"]}"'
        
        # Sec-CH-UA-Mobile
        headers['sec-ch-ua-mobile'] = '?0' if 'Desktop' in fp['platform'] else '?1'
        
        # 其他客户端提示头部
        if random.random() > 0.3:
            headers['sec-ch-viewport-width'] = str(int(fp['screen_res'].split('x')[0]))
            headers['viewport-width'] = str(int(fp['screen_res'].split('x')[0]))
        
        # 时区头部
        headers['timezone-offset'] = '480'  # UTC+8
        
        return headers
    
    def load_cookies(self):
        """从文件加载Cookies"""
        try:
            import json
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for domain, cookie_list in data.items():
                for cookie_data in cookie_list:
                    expires = None
                    if cookie_data.get('expires'):
                        expires = datetime.fromisoformat(cookie_data['expires'])
                    
                    cookie = Cookie(
                        name=cookie_data['name'],
                        value=cookie_data['value'],
                        domain=cookie_data['domain'],
                        path=cookie_data.get('path', '/'),
                        expires=expires,
                        secure=cookie_data.get('secure', False),
                        http_only=cookie_data.get('http_only', False),
                        same_site=cookie_data.get('same_site', 'Lax')
                    )
                    self.add_cookie(cookie)
            
            logger.info(f"从{self.cookie_file}加载了{sum(len(v) for v in self.cookies.values())}个Cookies")
            
        except FileNotFoundError:
            logger.info(f"Cookie文件不存在: {self.cookie_file}")
        except Exception as e:
            logger.error(f"加载Cookies失败: {e}")
    
    def save_cookies(self):
        """保存Cookies到文件"""
        if not self.cookie_file:
            return
        
        try:
            import json
            data = {}
            
            for domain, cookie_list in self.cookies.items():
                data[domain] = []
                for cookie in cookie_list:
                    cookie_data = {
                        'name': cookie.name,
                        'value': cookie.value,
                        'domain': cookie.domain,
                        'path': cookie.path,
                        'secure': cookie.secure,
                        'http_only': cookie.http_only,
                        'same_site': cookie.same_site
                    }
                    if cookie.expires:
                        cookie_data['expires'] = cookie.expires.isoformat()
                    data[domain].append(cookie_data)
            
            with open(self.cookie_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"保存了{sum(len(v) for v in self.cookies.values())}个Cookies到{self.cookie_file}")
            
        except Exception as e:
            logger.error(f"保存Cookies失败: {e}")


class HeadersManager:
    """请求头管理器"""
    
    def __init__(self):
        """初始化请求头管理器"""
        self.profiles: Dict[str, HeaderProfile] = {}
        self.current_profile: Optional[str] = None
        
        # 初始化默认配置文件
        self._init_default_profiles()
        
        # 尝试初始化fake_useragent
        try:
            self.ua = UserAgent()
        except Exception:
            self.ua = None
            logger.warning("fake_useragent初始化失败，将使用内置User-Agent列表")
    
    def _init_default_profiles(self):
        """初始化默认请求头配置"""
        
        # Chrome桌面版配置
        chrome_desktop = HeaderProfile(
            name="chrome_desktop",
            base_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'DNT': '1',
                'Upgrade-Insecure-Requests': '1',
            },
            user_agents=self._get_chrome_user_agents(),
            referer_templates=[
                'https://www.google.com/search?q=sports+lottery+{timestamp}',
                'https://www.baidu.com/s?wd=竞彩足球+{timestamp}',
                'https://www.lottery.gov.cn/',
                'https://www.sporttery.cn/'
            ],
            accept_languages=['zh-CN,zh;q=0.9', 'zh;q=0.9', 'en-US,en;q=0.9'],
            platforms=['desktop']
        )
        
        # Chrome移动版配置
        chrome_mobile = HeaderProfile(
            name="chrome_mobile",
            base_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,mobile',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'DNT': '1',
                'Upgrade-Insecure-Requests': '1',
                'X-Requested-With': 'XMLHttpRequest',
            },
            user_agents=self._get_chrome_mobile_user_agents(),
            referer_templates=[
                'https://m.baidu.com/s?word=竞彩足球',
                'https://m.sporttery.cn/',
                'https://www.lottery.gov.cn/mobile/'
            ],
            accept_languages=['zh-CN,zh;q=0.9', 'zh;q=0.8'],
            platforms=['mobile']
        )
        
        # Firefox桌面版配置
        firefox_desktop = HeaderProfile(
            name="firefox_desktop",
            base_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
            user_agents=self._get_firefox_user_agents(),
            referer_templates=[
                'https://www.google.com/search?q=football+lottery',
                'https://www.lottery.gov.cn/'
            ],
            accept_languages=['zh-CN,zh;q=0.8,en-US;q=0.5'],
            platforms=['desktop']
        )
        
        self.profiles[chrome_desktop.name] = chrome_desktop
        self.profiles[chrome_mobile.name] = chrome_mobile
        self.profiles[firefox_desktop.name] = firefox_desktop
        
        # 默认使用Chrome桌面版
        self.current_profile = chrome_desktop.name
    
    def _get_chrome_user_agents(self) -> List[str]:
        """获取Chrome桌面版User-Agent列表"""
        if self.ua:
            try:
                return [self.ua.chrome for _ in range(10)]
            except Exception:
                pass
        
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]
    
    def _get_chrome_mobile_user_agents(self) -> List[str]:
        """获取Chrome移动版User-Agent列表"""
        if self.ua:
            try:
                return [self.ua.chrome for _ in range(5)]  # mobile version
            except Exception:
                pass
        
        return [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        ]
    
    def _get_firefox_user_agents(self) -> List[str]:
        """获取Firefox桌面版User-Agent列表"""
        if self.ua:
            try:
                return [self.ua.firefox for _ in range(5)]
            except Exception:
                pass
        
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        ]
    
    def generate_headers(self, profile_name: str = None, platform: str = "desktop") -> Dict[str, str]:
        """生成请求头"""
        if profile_name and profile_name in self.profiles:
            profile = self.profiles[profile_name]
            self.current_profile = profile_name
        elif self.current_profile and self.current_profile in self.profiles:
            profile = self.profiles[self.current_profile]
        else:
            profile = list(self.profiles.values())[0]
            self.current_profile = profile.name
        
        # 生成基础头部
        headers = profile.generate_headers(platform)
        
        # 添加浏览器指纹
        headers = CookieManager().get_headers_with_fingerlogger.debug(headers)
        
        # 随机化一些头部顺序和值
        if random.random() > 0.7:
            # 随机添加一些额外的头部
            extra_headers = {
                'Pragma': 'no-cache',
                'Expires': '0',
            }
            headers.update(extra_headers)
        
        return headers
    
    def rotate_profile(self):
        """轮换到下一个配置文件"""
        profile_names = list(self.profiles.keys())
        if len(profile_names) <= 1:
            return
        
        current_idx = profile_names.index(self.current_profile) if self.current_profile else -1
        next_idx = (current_idx + 1) % len(profile_names)
        self.current_profile = profile_names[next_idx]
        
        logger.debug(f"轮换到配置文件: {self.current_profile}")
    
    def get_current_profile_info(self) -> Dict[str, Any]:
        """获取当前配置文件信息"""
        if not self.current_profile or self.current_profile not in self.profiles:
            return {}
        
        profile = self.profiles[self.current_profile]
        return {
            'name': profile.name,
            'platforms': profile.platforms,
            'user_agent_count': len(profile.user_agents),
            'referer_count': len(profile.referer_templates)
        }


# 全局实例
def get_headers_manager() -> HeadersManager:
    """获取全局请求头管理器"""
    return HeadersManager()

def get_cookie_manager(cookie_file: str = None) -> CookieManager:
    """获取全局Cookie管理器"""
    return CookieManager(cookie_file)