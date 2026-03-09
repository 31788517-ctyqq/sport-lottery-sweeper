"""
增强版高性能爬虫引擎
支持完整的反爬虫对策：代理池、请求头伪装、Cookie管理、指纹伪造
"""
import asyncio
import logging
import random
from typing import Dict, List, Optional, Any, Callable
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import aiohttp
from aiohttp import ClientTimeout, ClientSession, TCPConnector
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)


try:
    from aiolimiter import AsyncLimiter
except ImportError:
    AsyncLimiter = None

try:
    from aiocache import cached, Cache
    from aiocache.serializers import JsonSerializer
except ImportError:
    cached = None
    Cache = None

# 导入反爬虫模块
from .proxy_pool import get_proxy_pool, ProxyPool
from .headers_manager import get_headers_manager, get_cookie_manager, HeadersManager, CookieManager

logger = logging.getLogger(__name__)


class EnhancedScraperEngine:
    """
    增强版高性能爬虫引擎核心类
    
    特性:
    - 异步HTTP请求（aiohttp）
    - 连接池管理
    - 请求重试机制（tenacity）
    - 速率限制（aiolimiter）
    - 结果缓存（aiocache）
    - 完整反爬虫对策（代理池、请求头伪装、Cookie管理、指纹伪造）
    - 智能User-Agent轮换
    - 浏览器指纹伪造
    - 动态Cookie管理
    """
    
    def __init__(
        self,
        max_connections: int = 100,
        timeout: int = 15,
        max_retries: int = 3,
        rate_limit: Optional[int] = 10,  # 每秒最大请求数
        enable_cache: bool = True,
        cache_ttl: int = 300,  # 缓存5分钟
        proxy_urls: Optional[List[str]] = None,
        cookie_file: Optional[str] = None,
        header_profile: str = "chrome_desktop",
        enable_fingerprint: bool = True,
        rotation_interval: int = 50  # 每50个请求轮换一次配置
    ):
        """
        初始化增强爬虫引擎
        
        Args:
            max_connections: 最大并发连接数
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            rate_limit: 速率限制（请求/秒）
            enable_cache: 是否启用缓存
            cache_ttl: 缓存过期时间（秒）
            proxy_urls: 代理URL列表
            cookie_file: Cookie存储文件路径
            header_profile: 请求头配置文件名
            enable_fingerprint: 是否启用浏览器指纹伪造
            rotation_interval: 配置轮换间隔（请求数）
        """
        self.max_connections = max_connections
        self.timeout = ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.enable_cache = enable_cache and Cache is not None
        self.cache_ttl = cache_ttl
        
        # 反爬虫组件
        self.proxy_pool = get_proxy_pool()
        self.headers_manager = get_headers_manager()
        self.cookie_manager = get_cookie_manager(cookie_file)
        
        # 配置参数
        self.header_profile = header_profile
        self.enable_fingerprint = enable_fingerprint
        self.rotation_interval = rotation_interval
        self.request_counter = 0
        
        # 初始化代理池
        if proxy_urls:
            for proxy_url in proxy_urls:
                self.proxy_pool.add_proxy(proxy_url)
        
        # 连接池
        self.connector = TCPConnector(
            limit=max_connections,
            limit_per_host=30,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        self.session: Optional[ClientSession] = None
        
        # 速率限制器
        if rate_limit and AsyncLimiter:
            self.rate_limiter = AsyncLimiter(max_rate=rate_limit, time_period=1)
        else:
            self.rate_limiter = None
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cache_hits': 0,
            'retries': 0,
            'proxy_requests': 0,
            'direct_requests': 0,
            'fingerprint_requests': 0
        }
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    async def start(self):
        """启动引擎"""
        if self.session is None or self.session.closed:
            self.session = ClientSession(
                connector=self.connector,
                timeout=self.timeout,
                headers=self._get_base_headers()
            )
        
        # 启动代理池健康检查
        await self.proxy_pool.start_health_check_loop()
        
        logger.info(
            f"增强爬虫引擎已启动 [连接池={self.max_connections}, 超时={self.timeout.total}s, "
            f"代理池={len(self.proxy_pool.proxies)}, 指纹={self.enable_fingerprint}]"
        )
    
    async def close(self):
        """关闭引擎"""
        if self.session and not self.session.closed:
            await self.session.close()
        
        # 停止代理池健康检查
        await self.proxy_pool.stop_health_check_loop()
        
        # 保存Cookies
        self.cookie_manager.save_cookies()
        
        logger.info(f"增强爬虫引擎已关闭 [统计={self.stats}]")
    
    def _get_base_headers(self) -> Dict[str, str]:
        """获取基础请求头"""
        return {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
    
    def _should_rotate_config(self) -> bool:
        """判断是否应该轮换配置"""
        self.request_counter += 1
        return self.request_counter % self.rotation_interval == 0
    
    def _build_advanced_headers(self, url: str, custom_headers: Optional[Dict] = None) -> Dict[str, str]:
        """构建高级请求头（包含反爬虫对策）"""
        # 轮换配置（如果需要）
        if self._should_rotate_config():
            self.headers_manager.rotate_profile()
            logger.debug(f"轮换请求头配置到: {self.headers_manager.current_profile}")
        
        # 生成基础头部（包含指纹）
        if self.enable_fingerprint:
            headers = self.headers_manager.generate_headers(
                profile_name=self.header_profile,
                platform=random.choice(['desktop', 'mobile'])
            )
            self.stats['fingerprint_requests'] += 1
        else:
            headers = self.headers_manager.generate_headers(
                profile_name=self.header_profile
            )
        
        # 添加目标域名相关头部
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # 添加该域名的Cookies
        cookies = self.cookie_manager.get_cookies_for_domain(domain)
        if cookies:
            cookie_str = '; '.join([f'{k}={v}' for k, v in cookies.items()])
            headers['Cookie'] = cookie_str
        
        # 添加一些随机的安全头部
        security_headers = {
            'Sec-Fetch-Dest': random.choice(['document', 'empty', 'image', 'script']),
            'Sec-Fetch-Mode': random.choice(['navigate', 'cors', 'no-cors', 'same-origin']),
            'Sec-Fetch-Site': random.choice(['same-origin', 'same-site', 'cross-site', 'none']),
            'Sec-Fetch-User': '?1' if random.random() > 0.8 else None,
        }
        
        for key, value in security_headers.items():
            if value:
                headers[key] = value
        
        # 合并自定义头部
        if custom_headers:
            headers.update(custom_headers)
        
        return headers
    
    def _get_optimal_proxy(self) -> Optional[str]:
        """获取最优代理"""
        # 优先选择评分最高的代理
        proxy = self.proxy_pool.get_best_proxy()
        if proxy:
            self.stats['proxy_requests'] += 1
            return proxy.url
        
        # 如果没有最佳代理，随机选择一个健康的
        proxy = self.proxy_pool.get_random_proxy()
        if proxy:
            self.stats['proxy_requests'] += 1
            return proxy.url
        
        self.stats['direct_requests'] += 1
        return None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
    )
    async def _fetch_with_retry(
        self,
        url: str,
        method: str = 'GET',
        headers: Optional[Dict] = None,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """
        带重试的HTTP请求（增强版）
        
        使用tenacity实现指数退避重试
        """
        self.stats['retries'] += 1
        
        # 构建高级请求头
        final_headers = self._build_advanced_headers(url, headers)
        
        # 获取代理
        proxy_url = self._get_optimal_proxy()
        
        # 应用速率限制
        if self.rate_limiter:
            async with self.rate_limiter:
                return await self._do_request(url, method, final_headers, proxy_url, **kwargs)
        else:
            return await self._do_request(url, method, final_headers, proxy_url, **kwargs)
    
    async def _do_request(
        self,
        url: str,
        method: str,
        headers: Dict,
        proxy_url: Optional[str],
        **kwargs
    ) -> aiohttp.ClientResponse:
        """执行HTTP请求（增强版）"""
        request_kwargs = {
            'method': method,
            'url': url,
            'headers': headers,
            'proxy': proxy_url,
        }
        
        # 添加SSL验证选项（某些代理可能需要）
        if proxy_url and ('https' in proxy_url or 'socks' in proxy_url):
            request_kwargs['ssl'] = False
        
        request_kwargs.update(kwargs)
        
        async with self.session.request(**request_kwargs) as response:
            response.raise_for_status()
            
            # 更新Cookie
            self.cookie_manager.update_from_response(url, dict(response.headers))
            
            return response
    
    async def fetch(
        self,
        url: str,
        method: str = 'GET',
        headers: Optional[Dict] = None,
        cache_key: Optional[str] = None,
        update_proxy_stats: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        获取URL内容（增强版）
        
        Args:
            url: 目标URL
            method: HTTP方法
            headers: 自定义请求头
            cache_key: 缓存键（如果启用缓存）
            update_proxy_stats: 是否更新代理统计
            **kwargs: 其他aiohttp参数
            
        Returns:
            响应数据字典，包含 status, text, json, headers, cookies 等
        """
        self.stats['total_requests'] += 1
        
        # 检查缓存
        if self.enable_cache and cache_key:
            cached_data = await self._get_from_cache(cache_key)
            if cached_data:
                self.stats['cache_hits'] += 1
                logger.debug(f"缓存命中: {cache_key}")
                return cached_data
        
        proxy_url_used = None
        
        try:
            response = await self._fetch_with_retry(url, method, headers, **kwargs)
            proxy_url_used = response.connection._proxy if hasattr(response.connection, '_proxy') else None
            
            # 读取响应内容
            text = await response.text()
            
            result = {
                'status': response.status,
                'url': str(response.url),
                'headers': dict(response.headers),
                'cookies': dict(response.cookies) if response.cookies else {},
                'text': text,
                'timestamp': datetime.now().isoformat(),
                'proxy_used': proxy_url_used,
                'user_agent': response.request_info.headers.get('User-Agent', '') if response.request_info else ''
            }
            
            # 尝试解析JSON
            if 'application/json' in response.headers.get('Content-Type', ''):
                try:
                    result['json'] = await response.json()
                except Exception:
                    pass
            
            self.stats['successful_requests'] += 1
            
            # 更新代理统计
            if update_proxy_stats and proxy_url_used:
                success = response.status == 200
                response_time = None
                if 'X-Response-Time' in response.headers:
                    try:
                        response_time = float(response.headers['X-Response-Time'])
                    except ValueError:
                        pass
                await self.proxy_pool.update_proxy_stats(proxy_url_used, success, response_time)
            
            # 保存到缓存
            if self.enable_cache and cache_key:
                await self._save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"请求失败: {url}, 代理: {proxy_url_used}, 错误: {e}")
            
            # 更新代理统计（失败）
            if update_proxy_stats and proxy_url_used:
                await self.proxy_pool.update_proxy_stats(proxy_url_used, False)
            
            raise
    
    async def fetch_batch(
        self,
        urls: List[str],
        max_concurrent: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        批量获取URL（增强版）
        
        Args:
            urls: URL列表
            max_concurrent: 最大并发数
            **kwargs: 传递给fetch的参数
            
        Returns:
            响应列表
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_semaphore(url):
            async with semaphore:
                try:
                    return await self.fetch(url, **kwargs)
                except Exception as e:
                    logger.error(f"批量请求失败: {url}, 错误: {e}")
                    return None
        
        tasks = [fetch_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤掉None和异常
        return [r for r in results if r is not None and not isinstance(r, Exception)]
    
    async def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """从缓存获取数据"""
        if not self.enable_cache:
            return None
        
        try:
            cache = Cache(Cache.MEMORY)
            return await cache.get(key)
        except Exception as e:
            logger.warning(f"缓存读取失败: {e}")
            return None
    
    async def _save_to_cache(self, key: str, data: Dict[str, Any]):
        """保存数据到缓存"""
        if not self.enable_cache:
            return
        
        try:
            cache = Cache(Cache.MEMORY)
            await cache.set(key, data, ttl=self.cache_ttl)
        except Exception as e:
            logger.warning(f"缓存写入失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息（增强版）"""
        stats = self.stats.copy()
        if stats['total_requests'] > 0:
            stats['success_rate'] = round(
                stats['successful_requests'] / stats['total_requests'] * 100, 2
            )
            stats['cache_hit_rate'] = round(
                stats['cache_hits'] / stats['total_requests'] * 100, 2
            )
            stats['proxy_usage_rate'] = round(
                stats['proxy_requests'] / stats['total_requests'] * 100, 2
            )
        
        # 添加代理池统计
        stats['proxy_pool_stats'] = self.proxy_pool.get_stats()
        
        # 添加请求头配置信息
        stats['headers_profile'] = self.headers_manager.get_current_profile_info()
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查（增强版）"""
        health_info = {
            'engine_status': 'healthy',
            'session_active': self.session and not self.session.closed,
            'proxy_pool_healthy': len(self.proxy_pool.healthy_proxies) > 0,
            'headers_manager_ready': True,
            'cookie_manager_ready': True
        }
        
        # 检查代理池健康状态
        proxy_stats = self.proxy_pool.get_stats()
        health_info['proxy_pool_stats'] = proxy_stats
        
        # 检查会话状态
        if not health_info['session_active']:
            health_info['engine_status'] = 'unhealthy'
        
        # 检查是否有可用代理
        if not health_info['proxy_pool_healthy']:
            health_info['engine_status'] = 'degraded'
        
        return health_info


# 向后兼容性别名
ScraperEngine = EnhancedScraperEngine

# 创建全局单例
_global_engine: Optional[EnhancedScraperEngine] = None


async def get_engine() -> EnhancedScraperEngine:
    """获取全局爬虫引擎实例"""
    global _global_engine
    if _global_engine is None:
        _global_engine = EnhancedScraperEngine()
        await _global_engine.start()
    return _global_engine


async def close_engine():
    """关闭全局引擎"""
    global _global_engine
    if _global_engine:
        await _global_engine.close()
        _global_engine = None