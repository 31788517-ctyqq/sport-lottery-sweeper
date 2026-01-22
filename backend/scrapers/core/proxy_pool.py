"""
代理IP池管理模块
支持代理健康检查、性能评分、自动轮换
"""
import asyncio
import logging
import random
import time
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import aiohttp
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class ProxyStats:
    """代理统计信息"""
    success_count: int = 0
    failure_count: int = 0
    total_response_time: float = 0.0
    avg_response_time: float = 0.0
    last_used: Optional[datetime] = None
    last_success: Optional[datetime] = None
    consecutive_failures: int = 0
    banned_until: Optional[datetime] = None
    score: float = 100.0  # 代理评分 (0-100)


@dataclass
class Proxy:
    """代理配置"""
    url: str
    protocol: str = field(init=False)
    host: str = field(init=False)
    port: int = field(init=False)
    username: Optional[str] = None
    password: Optional[str] = None
    stats: ProxyStats = field(default_factory=ProxyStats)
    
    def __post_init__(self):
        """解析代理URL"""
        parsed = urlparse(self.url)
        self.protocol = parsed.scheme or 'http'
        self.host = parsed.hostname
        self.port = parsed.port or (443 if self.protocol == 'https' else 80)
        
        # 提取认证信息
        if parsed.username and parsed.password:
            self.username = parsed.username
            self.password = parsed.password


class ProxyPool:
    """代理IP池管理器"""
    
    def __init__(
        self,
        proxies: List[str] = None,
        health_check_interval: int = 300,  # 5分钟检查一次
        max_failures: int = 5,  # 连续失败5次标记为不可用
        ban_duration: int = 1800,  # 封禁30分钟
        min_score: float = 20.0,  # 最低评分阈值
        test_url: str = "http://httpbin.org/ip",
        test_timeout: int = 10
    ):
        """
        初始化代理池
        
        Args:
            proxies: 代理URL列表
            health_check_interval: 健康检查间隔(秒)
            max_failures: 最大连续失败次数
            ban_duration: 封禁时长(秒)
            min_score: 最低评分阈值
            test_url: 健康检查URL
            test_timeout: 检查超时时间
        """
        self.proxies: Dict[str, Proxy] = {}
        self.healthy_proxies: List[str] = []
        self.unhealthy_proxies: List[str] = []
        
        # 配置参数
        self.health_check_interval = health_check_interval
        self.max_failures = max_failures
        self.ban_duration = ban_duration
        self.min_score = min_score
        self.test_url = test_url
        self.test_timeout = test_timeout
        
        # 运行状态
        self.last_health_check: Optional[datetime] = None
        self.health_check_task: Optional[asyncio.Task] = None
        
        # 添加初始代理
        if proxies:
            for proxy_url in proxies:
                self.add_proxy(proxy_url)
    
    def add_proxy(self, proxy_url: str) -> bool:
        """添加代理"""
        try:
            proxy = Proxy(proxy_url)
            self.proxies[proxy_url] = proxy
            logger.info(f"添加代理: {proxy_url} ({proxy.host}:{proxy.port})")
            return True
        except Exception as e:
            logger.error(f"添加代理失败 {proxy_url}: {e}")
            return False
    
    def remove_proxy(self, proxy_url: str) -> bool:
        """移除代理"""
        if proxy_url in self.proxies:
            del self.proxies[proxy_url]
            if proxy_url in self.healthy_proxies:
                self.healthy_proxies.remove(proxy_url)
            if proxy_url in self.unhealthy_proxies:
                self.unhealthy_proxies.remove(proxy_url)
            logger.info(f"移除代理: {proxy_url}")
            return True
        return False
    
    def get_random_proxy(self, exclude_banned: bool = True) -> Optional[Proxy]:
        """获取随机代理(基于评分权重)"""
        available_proxies = []
        weights = []
        
        for proxy_url, proxy in self.proxies.items():
            # 排除被封禁的代理
            if exclude_banned and proxy.stats.banned_until:
                if datetime.now() < proxy.stats.banned_until:
                    continue
                else:
                    proxy.stats.banned_until = None
            
            # 排除评分过低的代理
            if proxy.stats.score < self.min_score:
                continue
            
            # 排除连续失败的代理
            if proxy.stats.consecutive_failures >= self.max_failures:
                continue
            
            available_proxies.append(proxy_url)
            # 使用评分作为权重(评分越高，被选中的概率越大)
            weight = max(proxy.stats.score, 1.0)
            weights.append(weight)
        
        if not available_proxies:
            logger.warning("没有可用的健康代理")
            return None
        
        # 加权随机选择
        chosen_url = random.choices(available_proxies, weights=weights)[0]
        proxy = self.proxies[chosen_url]
        proxy.stats.last_used = datetime.now()
        
        return proxy
    
    def get_best_proxy(self) -> Optional[Proxy]:
        """获取评分最高的代理"""
        best_proxy = None
        best_score = -1
        
        for proxy_url, proxy in self.proxies.items():
            if (proxy.stats.score > best_score and 
                proxy.stats.score >= self.min_score and
                (not proxy.stats.banned_until or datetime.now() >= proxy.stats.banned_until)):
                best_score = proxy.stats.score
                best_proxy = proxy
        
        if best_proxy:
            best_proxy.stats.last_used = datetime.now()
        
        return best_proxy
    
    async def test_proxy(self, proxy: Proxy) -> Tuple[bool, float]:
        """测试代理连通性"""
        start_time = time.time()
        
        try:
            # 构建代理URL(包含认证信息)
            proxy_url = proxy.url
            if proxy.username and proxy.password:
                # aiohttp会自动处理URL中的认证信息
                pass
            
            timeout = aiohttp.ClientTimeout(total=self.test_timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(self.test_url, proxy=proxy_url) as response:
                    if response.status == 200:
                        response_time = time.time() - start_time
                        return True, response_time
                    else:
                        return False, time.time() - start_time
                        
        except Exception as e:
            response_time = time.time() - start_time
            logger.debug(f"代理测试失败 {proxy.url}: {e}")
            return False, response_time
    
    async def update_proxy_stats(self, proxy_url: str, success: bool, response_time: float = None):
        """更新代理统计信息"""
        if proxy_url not in self.proxies:
            return
        
        proxy = self.proxies[proxy_url]
        stats = proxy.stats
        
        if success:
            stats.success_count += 1
            stats.consecutive_failures = 0
            stats.last_success = datetime.now()
            
            # 解除封禁
            if stats.banned_until and datetime.now() >= stats.banned_until:
                stats.banned_until = None
        else:
            stats.failure_count += 1
            stats.consecutive_failures += 1
            
            # 连续失败过多，暂时封禁
            if stats.consecutive_failures >= self.max_failures:
                stats.banned_until = datetime.now() + timedelta(seconds=self.ban_duration)
                logger.warning(f"代理被封禁 {proxy_url}: 连续失败{stats.consecutive_failures}次")
        
        # 更新响应时间统计
        if response_time is not None:
            stats.total_response_time += response_time
            stats.avg_response_time = stats.total_response_time / (stats.success_count + stats.failure_count)
        
        # 计算评分 (0-100)
        stats.score = self._calculate_proxy_score(proxy)
        
        # 更新健康状态
        self._update_health_status(proxy_url)
    
    def _calculate_proxy_score(self, proxy: Proxy) -> float:
        """计算代理评分"""
        stats = proxy.stats
        
        if stats.success_count + stats.failure_count == 0:
            return 100.0  # 新代理默认满分
        
        # 基础成功率评分
        total_requests = stats.success_count + stats.failure_count
        success_rate = stats.success_count / total_requests
        base_score = success_rate * 60  # 成功率占60分
        
        # 响应时间评分 (越快分数越高)
        speed_score = 0
        if stats.avg_response_time > 0:
            # 响应时间越短分数越高，3秒以内为优秀
            if stats.avg_response_time <= 1:
                speed_score = 25
            elif stats.avg_response_time <= 2:
                speed_score = 20
            elif stats.avg_response_time <= 3:
                speed_score = 15
            elif stats.avg_response_time <= 5:
                speed_score = 10
            else:
                speed_score = 5
        
        # 稳定性评分 (连续失败惩罚)
        stability_score = max(0, 15 - (stats.consecutive_failures * 3))
        
        # 使用频率奖励 (适度使用加分)
        usage_score = min(10, total_requests * 0.1)
        
        final_score = base_score + speed_score + stability_score + usage_score
        return max(0, min(100, final_score))
    
    def _update_health_status(self, proxy_url: str):
        """更新代理健康状态"""
        proxy = self.proxies[proxy_url]
        
        was_healthy = proxy_url in self.healthy_proxies
        
        # 判断是否为健康代理
        is_healthy = (
            proxy.stats.score >= self.min_score and
            proxy.stats.consecutive_failures < self.max_failures and
            (not proxy.stats.banned_until or datetime.now() >= proxy.stats.banned_until)
        )
        
        if is_healthy and not was_healthy:
            self.healthy_proxies.append(proxy_url)
            if proxy_url in self.unhealthy_proxies:
                self.unhealthy_proxies.remove(proxy_url)
            logger.info(f"代理恢复健康: {proxy_url} (评分:{proxy.stats.score:.1f})")
        elif not is_healthy and was_healthy:
            if proxy_url in self.healthy_proxies:
                self.healthy_proxies.remove(proxy_url)
            self.unhealthy_proxies.append(proxy_url)
            logger.warning(f"代理变为不健康: {proxy_url} (评分:{proxy.stats.score:.1f})")
    
    async def health_check_all(self) -> Dict[str, Any]:
        """对所有代理进行健康检查"""
        logger.info(f"开始健康检查，共{len(self.proxies)}个代理")
        
        tasks = []
        for proxy_url, proxy in self.proxies.items():
            # 跳过最近刚检查过的代理
            if (proxy.stats.last_used and 
                datetime.now() - proxy.stats.last_used < timedelta(seconds=60)):
                continue
            
            task = self._check_single_proxy(proxy)
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self.last_health_check = datetime.now()
        
        # 返回检查结果统计
        healthy_count = len(self.healthy_proxies)
        total_count = len(self.proxies)
        
        logger.info(f"健康检查完成: {healthy_count}/{total_count} 个代理健康")
        
        return {
            'total': total_count,
            'healthy': healthy_count,
            'unhealthy': len(self.unhealthy_proxies),
            'healthy_proxies': self.healthy_proxies,
            'unhealthy_proxies': self.unhealthy_proxies
        }
    
    async def _check_single_proxy(self, proxy: Proxy):
        """检查单个代理"""
        try:
            success, response_time = await self.test_proxy(proxy)
            await self.update_proxy_stats(proxy.url, success, response_time)
        except Exception as e:
            logger.error(f"代理检查异常 {proxy.url}: {e}")
            await self.update_proxy_stats(proxy.url, False)
    
    async def start_health_check_loop(self):
        """启动健康检查循环"""
        if self.health_check_task and not self.health_check_task.done():
            return
        
        async def health_check_loop():
            while True:
                try:
                    await self.health_check_all()
                    await asyncio.sleep(self.health_check_interval)
                except Exception as e:
                    logger.error(f"健康检查循环异常: {e}")
                    await asyncio.sleep(60)  # 出错后等待1分钟再试
        
        self.health_check_task = asyncio.create_task(health_check_loop())
        logger.info("启动代理健康检查循环")
    
    async def stop_health_check_loop(self):
        """停止健康检查循环"""
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
            self.health_check_task = None
            logger.info("停止代理健康检查循环")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取代理池统计信息"""
        stats = {
            'total_proxies': len(self.proxies),
            'healthy_proxies': len(self.healthy_proxies),
            'unhealthy_proxies': len(self.unhealthy_proxies),
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None
        }
        
        # 各代理详细信息
        proxy_details = {}
        for proxy_url, proxy in self.proxies.items():
            proxy_details[proxy_url] = {
                'protocol': proxy.protocol,
                'host': proxy.host,
                'port': proxy.port,
                'score': round(proxy.stats.score, 2),
                'success_count': proxy.stats.success_count,
                'failure_count': proxy.stats.failure_count,
                'avg_response_time': round(proxy.stats.avg_response_time, 3),
                'consecutive_failures': proxy.stats.consecutive_failures,
                'banned_until': proxy.stats.banned_until.isoformat() if proxy.stats.banned_until else None,
                'healthy': proxy_url in self.healthy_proxies
            }
        
        stats['proxy_details'] = proxy_details
        return stats


# 全局代理池实例
_global_proxy_pool: Optional[ProxyPool] = None


async def get_proxy_pool() -> ProxyPool:
    """获取全局代理池实例"""
    global _global_proxy_pool
    if _global_proxy_pool is None:
        _global_proxy_pool = ProxyPool()
        await _global_proxy_pool.start_health_check_loop()
    return _global_proxy_pool


async def close_proxy_pool():
    """关闭全局代理池"""
    global _global_proxy_pool
    if _global_proxy_pool:
        await _global_proxy_pool.stop_health_check_loop()
        _global_proxy_pool = None


if __name__ == "__main__":
    # 简单的测试代码
    async def test():
        pool = ProxyPool([
            "http://proxy1.example.com:8080",
            "http://proxy2.example.com:8080"
        ])
        print("代理池创建成功")
        stats = pool.get_stats()
        print(f"统计信息: {stats}")
    
    asyncio.run(test())