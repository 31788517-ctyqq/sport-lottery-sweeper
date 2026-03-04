"""
增强型爬虫引擎
集成IP代理模块，支持动态获取和使用89ip.cn的代理IP
"""
import asyncio
import logging
import random
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import aiohttp
from aiohttp import ClientTimeout, ClientSession
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

# 导入IP代理模块
from crawler.ip_proxy import IPProxyPool as IPProxyManager

logger = logging.getLogger(__name__)


class EnhancedScraperEngine:
    """
    增强型爬虫引擎
    
    特性:
    - 继承基础爬虫引擎的所有功能
    - 集成IPProxyManager，动态获取89ip.cn的代理IP
    - 支持代理IP的自动验证和轮换
    - 智能代理选择算法
    """
    
    # User-Agent池
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    ]
    
    def __init__(
        self,
        max_connections: int = 100,
        timeout: int = 15,
        max_retries: int = 3,
        rate_limit: Optional[int] = 10,  # 每秒最大请求数
        enable_cache: bool = True,
        cache_ttl: int = 300,  # 缓存5分钟
        use_dynamic_proxies: bool = True,  # 是否使用动态代理
        proxy_refresh_interval: int = 300  # 代理刷新间隔（秒）
    ):
        """
        初始化增强型爬虫引擎
        
        Args:
            max_connections: 最大并发连接数
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            rate_limit: 速率限制（请求/秒）
            enable_cache: 是否启用缓存
            cache_ttl: 缓存过期时间（秒）
            use_dynamic_proxies: 是否使用动态代理
            proxy_refresh_interval: 代理刷新间隔（秒）
        """
        self.max_connections = max_connections
        self.timeout = ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.enable_cache = enable_cache and Cache is not None
        self.cache_ttl = cache_ttl
        self.use_dynamic_proxies = use_dynamic_proxies
        self.proxy_refresh_interval = proxy_refresh_interval
        
        # 初始化IP代理管理器
        self.ip_proxy_manager = IPProxyManager() if use_dynamic_proxies else None
        
        # 本地代理池，用于存储从IP代理管理器获取的代理
        self.local_proxy_pool = []
        self.last_proxy_refresh = datetime.min
        
        # 连接池
        self.connector = aiohttp.TCPConnector(
            limit=max_connections,
            limit_per_host=30,
            ttl_dns_cache=300
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
            'proxy_switches': 0
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
                timeout=self.timeout
            )
        
        # 预先加载一些代理IP
        if self.use_dynamic_proxies and self.ip_proxy_manager:
            await self._refresh_proxy_pool()
        
        logger.info(f"增强型爬虫引擎已启动 [连接池={self.max_connections}, 超时={self.timeout.total}s, 代理数={len(self.local_proxy_pool)}]")
    
    async def close(self):
        """关闭引擎"""
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info(f"增强型爬虫引擎已关闭 [统计={self.stats}]")
    
    async def _refresh_proxy_pool(self):
        """刷新本地代理池"""
        if not self.use_dynamic_proxies or not self.ip_proxy_manager:
            return
        
        try:
            # 获取有效代理
            valid_proxies = self.ip_proxy_manager.get_valid_proxies(count=10)
            
            # 转换为aiohttp格式的代理字符串
            self.local_proxy_pool = []
            for proxy in valid_proxies:
                proxy_str = f"http://{proxy['ip']}:{proxy['port']}"
                self.local_proxy_pool.append(proxy_str)
            
            self.last_proxy_refresh = datetime.now()
            logger.info(f"代理池已刷新，当前有 {len(self.local_proxy_pool)} 个有效代理")
        except Exception as e:
            logger.error(f"刷新代理池失败: {str(e)}")
    
    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        return random.choice(self.USER_AGENTS)
    
    def _get_random_proxy(self) -> Optional[str]:
        """获取随机代理，如果启用动态代理则从IP代理管理器获取"""
        # 定期刷新代理池
        if (self.use_dynamic_proxies and 
            self.ip_proxy_manager and 
            (datetime.now() - self.last_proxy_refresh).seconds > self.proxy_refresh_interval):
            # 在异步环境中刷新代理池
            asyncio.create_task(self._refresh_proxy_pool())
        
        # 如果有本地代理池，则从中随机选择
        if self.local_proxy_pool:
            return random.choice(self.local_proxy_pool)
        
        # 如果没有可用代理，则返回None
        return None
    
    def _build_headers(self, custom_headers: Optional[Dict] = None) -> Dict:
        """构建请求头"""
        headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        if custom_headers:
            headers.update(custom_headers)
        return headers
    
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
        带重试的HTTP请求
        
        使用tenacity实现指数退避重试
        """
        self.stats['retries'] += 1
        
        # 应用速率限制
        if self.rate_limiter:
            async with self.rate_limiter:
                return await self._do_request(url, method, headers, **kwargs)
        else:
            return await self._do_request(url, method, headers, **kwargs)
    
    async def _do_request(
        self,
        url: str,
        method: str,
        headers: Optional[Dict],
        **kwargs
    ) -> aiohttp.ClientResponse:
        """执行HTTP请求"""
        final_headers = self._build_headers(headers)
        proxy = self._get_random_proxy()
        
        # 记录请求信息
        logger.debug(f"发起请求: {url}, 代理: {proxy if proxy else '无'}")
        
        async with self.session.request(
            method=method,
            url=url,
            headers=final_headers,
            proxy=proxy,
            **kwargs
        ) as response:
            response.raise_for_status()
            return response
    
    async def fetch(
        self,
        url: str,
        method: str = 'GET',
        headers: Optional[Dict] = None,
        cache_key: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        获取URL内容
        
        Args:
            url: 目标URL
            method: HTTP方法
            headers: 自定义请求头
            cache_key: 缓存键（如果启用缓存）
            **kwargs: 其他aiohttp参数
            
        Returns:
            响应数据字典，包含 status, text, json 等
        """
        self.stats['total_requests'] += 1
        
        # 检查缓存
        if self.enable_cache and cache_key:
            cached_data = await self._get_from_cache(cache_key)
            if cached_data:
                self.stats['cache_hits'] += 1
                logger.debug(f"缓存命中: {cache_key}")
                return cached_data
        
        try:
            response = await self._fetch_with_retry(url, method, headers, **kwargs)
            
            # 读取响应内容
            text = await response.text()
            
            result = {
                'status': response.status,
                'url': str(response.url),
                'headers': dict(response.headers),
                'text': text,
                'timestamp': datetime.now().isoformat()
            }
            
            # 尝试解析JSON
            if 'application/json' in response.headers.get('Content-Type', ''):
                try:
                    result['json'] = await response.json()
                except Exception:
                    pass
            
            self.stats['successful_requests'] += 1
            
            # 保存到缓存
            if self.enable_cache and cache_key:
                await self._save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"请求失败: {url}, 错误: {e}")
            
            # 如果请求失败且使用了代理，尝试更换代理重试
            if self.local_proxy_pool:
                logger.warning(f"请求失败，代理可能无效，尝试更换代理")
                self.stats['proxy_switches'] += 1
                # 重新获取代理列表
                await self._refresh_proxy_pool()
            
            raise
    
    async def fetch_batch(
        self,
        urls: List[str],
        max_concurrent: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        批量获取URL
        
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
        """获取统计信息"""
        stats = self.stats.copy()
        if stats['total_requests'] > 0:
            stats['success_rate'] = round(
                stats['successful_requests'] / stats['total_requests'] * 100, 2
            )
            stats['cache_hit_rate'] = round(
                stats['cache_hits'] / stats['total_requests'] * 100, 2
            )
        stats['active_proxies'] = len(self.local_proxy_pool)
        return stats


# 创建全局单例
_global_enhanced_engine: Optional[EnhancedScraperEngine] = None


async def get_enhanced_engine() -> EnhancedScraperEngine:
    """获取全局增强型爬虫引擎实例"""
    global _global_enhanced_engine
    if _global_enhanced_engine is None:
        _global_enhanced_engine = EnhancedScraperEngine()
        await _global_enhanced_engine.start()
    return _global_enhanced_engine


async def close_enhanced_engine():
    """关闭全局增强型引擎"""
    global _global_enhanced_engine
    if _global_enhanced_engine:
        await _global_enhanced_engine.close()
        _global_enhanced_engine = None