"""
IP代理池模块 - 增强版
包含IP质量评估、智能轮换、监控管理等功能
"""
import requests
import threading
import time
import random
from urllib.parse import urlparse
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import logging

# 导入新功能模块
from .integrated_ip_pool import IntegratedIPPool
from .ip_quality_assessment import QualityBasedProxyPool, ProxyIP
from .adaptive_proxy_rotator import AdvancedProxyManager
from .proxy_monitor import ProxyPoolManager
from .ip_fetcher_89ip import Ip89Fetcher, add_ips_from_89ip_to_pool  # 新增导入


@dataclass
class Proxy:
    """代理类"""
    ip: str
    port: int
    protocol: str = "http"
    country: str = ""
    anonymity: str = ""
    response_time: float = 0.0
    last_checked: float = 0.0
    is_active: bool = True

    @property
    def address(self) -> str:
        return f"{self.protocol}://{self.ip}:{self.port}"

    def __str__(self) -> str:
        return self.address


class IPProxyPool:
    """IP代理池 - 增强版"""
    
    def __init__(self, min_proxy_count: int = 10, max_proxy_count: int = 100):
        self.min_proxy_count = min_proxy_count
        self.max_proxy_count = max_proxy_count
        self.proxies: List[Proxy] = []
        self.active_proxies: List[Proxy] = []
        self.failed_proxies: List[Proxy] = []
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # 初始化集成IP池系统
        self.integrated_pool = IntegratedIPPool({
            'min_quality_score': 0.3,
            'validation_interval': 3600,
            'monitoring_interval': 60,
            'max_proxy_per_domain': 5,
            'request_delay_range': (1, 5),
            'retry_attempts': 3,
            'auto_expand_enabled': True,
            'expansion_threshold': 10
        })
        
        # 启动后台监控
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("IP代理池已初始化")

    @property
    def proxy_list(self):
        """兼容老代码的属性，返回简化后的代理信息列表"""
        return [
            {
                "ip": proxy.ip,
                "port": proxy.port,
                "protocol": proxy.protocol,
                "response_time": getattr(proxy, "response_time", None),
                "last_checked": getattr(proxy, "last_checked", None)
            }
            for proxy in self.proxies
        ]

    def refresh_proxy_pool(self, count: int = 15, validate: bool = False) -> int:
        """
        简单的刷新入口，默认从89ip抓取代理，兼容 DynamicProxyUpdater 的调用方式
        """
        pages = max(1, count // 5)
        return self.fetch_ips_from_89ip(pages=pages, validate=validate)

    def add_proxy(self, ip: str, port: int, protocol: str = "http") -> bool:
        """添加代理到池中"""
        with self.lock:
            # 检查是否已存在
            for proxy in self.proxies:
                if proxy.ip == ip and proxy.port == port:
                    self.logger.info(f"代理 {ip}:{port} 已存在")
                    return False
            
            proxy = Proxy(ip, port, protocol)
            self.proxies.append(proxy)
            self.integrated_pool.add_proxy(ip, port, protocol)
            
            self.logger.info(f"添加代理: {proxy.address}")
            return True

    def add_proxies_from_list(self, proxy_list: List[str]) -> int:
        """从列表添加多个代理"""
        added_count = 0
        for proxy_str in proxy_list:
            try:
                # 解析代理字符串 (格式: ip:port 或 protocol://ip:port)
                if "://" in proxy_str:
                    protocol, addr = proxy_str.split("://")
                    ip, port = addr.split(":")
                else:
                    protocol = "http"
                    ip, port = proxy_str.split(":")
                
                if self.add_proxy(ip, int(port), protocol):
                    added_count += 1
            except Exception as e:
                self.logger.error(f"添加代理失败 {proxy_str}: {e}")
        
        self.logger.info(f"成功添加 {added_count} 个代理")
        return added_count

    def remove_proxy(self, proxy: Proxy) -> bool:
        """从池中移除代理"""
        with self.lock:
            if proxy in self.proxies:
                self.proxies.remove(proxy)
                self.active_proxies = [p for p in self.active_proxies if p != proxy]
                self.logger.info(f"移除代理: {proxy.address}")
                return True
            return False

    def get_proxy(self, target_domain: Optional[str] = None) -> Optional[Proxy]:
        """获取一个可用的代理"""
        # 使用集成IP池的代理管理器
        try:
            # 如果有目标域名，让高级管理器选择最优代理
            if target_domain:
                proxy_obj = self.integrated_pool.advanced_manager.rotator.get_proxy(target_domain)
                if proxy_obj:
                    # 转换为本模块的Proxy类型
                    ip, port = proxy_obj.address.split('://')[1].split(':')
                    return Proxy(ip, int(port), proxy_obj.protocol)
            
            # 否则随机选择一个活动代理
            if self.active_proxies:
                return random.choice(self.active_proxies)
            
            # 如果没有活动代理，返回第一个代理
            if self.proxies:
                return self.proxies[0]
                
        except Exception as e:
            self.logger.error(f"获取代理时出错: {e}")
        
        return None

    def mark_proxy_failed(self, proxy: Proxy, target_domain: Optional[str] = None) -> bool:
        """标记代理为失败"""
        with self.lock:
            if proxy in self.active_proxies:
                self.active_proxies.remove(proxy)
            if proxy not in self.failed_proxies:
                self.failed_proxies.append(proxy)
        
        # 在集成池中标记失败
        try:
            proxy_obj = ProxyIP(proxy.ip, proxy.port, proxy.protocol)
            self.integrated_pool.advanced_manager.rotator.mark_proxy_failure(
                proxy_obj, target_domain
            )
        except Exception as e:
            self.logger.error(f"标记代理失败时出错: {e}")
        
        return True

    def mark_proxy_good(self, proxy: Proxy) -> bool:
        """标记代理为可用"""
        with self.lock:
            if proxy not in self.active_proxies:
                self.active_proxies.append(proxy)
            if proxy in self.failed_proxies:
                self.failed_proxies.remove(proxy)
        
        # 在集成池中标记成功
        try:
            proxy_obj = ProxyIP(proxy.ip, proxy.port, proxy.protocol)
            self.integrated_pool.advanced_manager.rotator.mark_proxy_success(proxy_obj)
        except Exception as e:
            self.logger.error(f"标记代理成功时出错: {e}")
        
        return True

    def validate_proxy(self, proxy: Proxy, timeout: int = 10) -> bool:
        """验证代理是否可用"""
        try:
            proxies = {
                "http": proxy.address,
                "https": proxy.address
            }
            
            start_time = time.time()
            response = requests.get(
                "http://httpbin.org/ip", 
                proxies=proxies, 
                timeout=timeout,
                headers={"User-Agent": "Mozilla/5.0 (compatible; ProxyValidator/1.0)"}
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # 更新响应时间
                proxy.response_time = response_time
                proxy.last_checked = time.time()
                self.logger.info(f"代理验证成功: {proxy.address}, 响应时间: {response_time:.2f}s")
                return True
        except Exception as e:
            self.logger.debug(f"代理验证失败: {proxy.address}, 错误: {e}")
        
        return False

    def validate_all_proxies(self):
        """验证所有代理"""
        self.logger.info("开始验证所有代理...")
        
        def validate_single_proxy(proxy: Proxy):
            if self.validate_proxy(proxy):
                self.mark_proxy_good(proxy)
            else:
                self.mark_proxy_failed(proxy)
        
        # 使用线程池验证代理
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(validate_single_proxy, proxy) for proxy in self.proxies]
            for future in futures:
                future.result()  # 等待所有验证完成
        
        self.logger.info(f"验证完成. 活跃代理: {len(self.active_proxies)}, 失败代理: {len(self.failed_proxies)}")

    def get_proxy_count(self) -> Dict[str, int]:
        """获取代理数量统计"""
        return {
            "total": len(self.proxies),
            "active": len(self.active_proxies),
            "failed": len(self.failed_proxies)
        }

    def _monitor_loop(self):
        """监控循环 - 后台运行"""
        while self.monitoring:
            try:
                # 定期验证代理
                time.sleep(300)  # 5分钟
                self.validate_all_proxies()
                
                # 检查是否需要补充代理
                counts = self.get_proxy_count()
                if counts['active'] < self.min_proxy_count:
                    self.logger.info(f"活跃代理数量不足 ({counts['active']} < {self.min_proxy_count}), 需要补充")
                    self._fetch_additional_proxies()
                    
            except Exception as e:
                self.logger.error(f"监控循环出错: {e}")

    def get_status(self) -> Dict[str, Any]:
        """获取IP池状态，包括集成池的状态"""
        basic_status = self.get_proxy_count()
        integrated_status = self.integrated_pool.get_status()
        
        return {
            "basic_stats": basic_status,
            "integrated_pool_stats": integrated_status,
            "active_proxies": [str(p) for p in self.active_proxies[:5]],  # 仅显示前5个
            "failed_proxies_count": len(self.failed_proxies),
            "last_updated": time.time()
        }

    def close(self):
        """关闭IP池"""
        self.monitoring = False
        self.integrated_pool.shutdown()  # 关闭集成池
        self.logger.info("IP代理池已关闭")

    def _fetch_additional_proxies(self):
        """获取额外的代理IP"""
        self.logger.info("开始从89ip.cn获取更多代理IP...")
        try:
            # 从89ip.cn获取IP并添加到池中
            added_count = add_ips_from_89ip_to_pool(
                ip_pool=self,
                pages=2,  # 获取前2页
                validate=True  # 验证IP可用性
            )
            self.logger.info(f"从89ip.cn成功添加了 {added_count} 个代理IP")
        except Exception as e:
            self.logger.error(f"从89ip.cn获取IP时出错: {str(e)}")

    def fetch_ips_from_89ip(self, pages: int = 3, validate: bool = True) -> int:
        """
        从89ip.cn获取IP并添加到IP池
        :param pages: 获取页面数量
        :param validate: 是否验证IP可用性
        :return: 成功添加的IP数量
        """
        self.logger.info(f"手动从89ip.cn获取IP，页数: {pages}")
        try:
            added_count = add_ips_from_89ip_to_pool(
                ip_pool=self,
                pages=pages,
                validate=validate
            )
            self.logger.info(f"手动从89ip.cn成功添加了 {added_count} 个代理IP")
            return added_count
        except Exception as e:
            self.logger.error(f"手动从89ip.cn获取IP时出错: {str(e)}")
            return 0


def test_enhanced_proxy_pool():
    """测试增强版代理池"""
    print("="*60)
    print("测试: 增强版IP代理池")
    print("="*60)
    
    # 创建代理池
    pool = IPProxyPool(min_proxy_count=5, max_proxy_count=50)
    
    # 添加一些示例代理
    sample_proxies = [
        "127.0.0.1:8080",
        "192.168.1.1:80", 
        "proxy.example.com:3128"
    ]
    
    print(f"添加示例代理: {sample_proxies}")
    added = pool.add_proxies_from_list(sample_proxies)
    print(f"成功添加 {added} 个代理")
    
    # 从89ip.cn获取IP
    print("\n从89ip.cn获取IP...")
    fetched_count = pool.fetch_ips_from_89ip(pages=1, validate=False)  # 为了测试，先不验证
    print(f"从89ip.cn获取并添加了 {fetched_count} 个IP")
    
    # 获取状态
    status = pool.get_status()
    print(f"\nIP池状态: {status}")
    
    # 尝试获取代理
    proxy = pool.get_proxy("example.com")
    if proxy:
        print(f"获取到代理: {proxy}")
    else:
        print("未获取到代理")
    
    # 模拟验证
    print("\n模拟验证代理...")
    if proxy:
        is_valid = pool.validate_proxy(proxy)
        print(f"代理 {proxy} 验证结果: {'有效' if is_valid else '无效'}")
    
    # 关闭池
    pool.close()
    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_enhanced_proxy_pool()
