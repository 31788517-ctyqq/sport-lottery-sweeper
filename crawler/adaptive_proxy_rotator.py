"""
智能代理轮换策略模块
实现自适应IP轮换算法
"""
import time
import random
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from .ip_quality_assessment import QualityBasedProxyPool, ProxyIP


class AdaptiveProxyRotator:
    """自适应代理轮换器"""
    
    def __init__(
        self, 
        proxy_pool: QualityBasedProxyPool, 
        min_interval: float = 5, 
        max_interval: float = 30,
        usage_limit_per_ip: int = 10,
        cool_down_period: int = 300  # 冷却时间(秒)
    ):
        self.proxy_pool = proxy_pool
        self.min_interval = min_interval  # 最小轮换间隔(秒)
        self.max_interval = max_interval  # 最大轮换间隔(秒)
        self.usage_limit_per_ip = usage_limit_per_ip  # 单个IP使用次数限制
        self.cool_down_period = cool_down_period  # 冷却时间(秒)
        
        # 记录IP使用情况
        self.last_rotation_time: Dict[str, float] = {}
        self.rotation_count: Dict[str, int] = {}
        self.last_use_time: Dict[str, float] = {}
        self.failed_domains: Dict[str, List[str]] = {}  # 记录IP在哪些域名上失败
        self.lock = threading.Lock()
        
    def calculate_priority_score(self, proxy: ProxyIP, domain: Optional[str] = None) -> float:
        """
        计算代理的优先级得分
        :param proxy: 代理IP对象
        :param domain: 目标域名
        :return: 优先级得分
        """
        # 基础评分：成功率 * 0.6 - 延迟 * 0.4
        base_score = proxy.metrics.success_rate * 0.6
        
        # 延迟评分：延迟越低越好，转换为0-1区间
        latency_score = 0.0
        if proxy.metrics.latency != float('inf'):
            # 假设最大延迟为5秒，转换为0-1评分
            latency_score = max(0, 1 - proxy.metrics.latency / 5000)
        
        base_score -= latency_score * 0.4
        
        # 时间因素：最近未使用的代理加分
        current_time = time.time()
        last_used = self.last_use_time.get(proxy.address, 0)
        time_factor = min((current_time - last_used) / 60, 5)  # 最多加5分
        
        # 如果该IP在特定域名上失败过，降低分数
        domain_penalty = 0
        if domain and proxy.address in self.failed_domains:
            if domain in self.failed_domains[proxy.address]:
                domain_penalty = 0.5  # 在特定域名上失败的惩罚
        
        # 使用频率惩罚：如果使用过于频繁，降低分数
        use_count = self.rotation_count.get(proxy.address, 0)
        frequency_penalty = min(use_count / self.usage_limit_per_ip, 0.3)  # 最多减0.3分
        
        # 综合评分
        total_score = base_score + time_factor * 0.1 - domain_penalty - frequency_penalty
        
        return total_score
    
    def get_proxy(self, domain: Optional[str] = None) -> Optional[ProxyIP]:
        """
        根据当前情况智能选择代理
        :param domain: 目标域名
        :return: 选择的代理IP
        """
        with self.lock:
            # 获取高质量代理列表
            available_proxies = self.proxy_pool.get_high_quality_proxies()
            
            if not available_proxies:
                print("⚠️  没有可用的高质量代理")
                return None
            
            # 计算每个代理的优先级得分
            proxy_scores = []
            current_time = time.time()
            
            for proxy in available_proxies:
                # 检查是否在冷却期内
                last_use = self.last_use_time.get(proxy.address, 0)
                if current_time - last_use < self.cool_down_period:
                    continue  # 跳过仍在冷却期的IP
                
                # 检查使用次数限制
                use_count = self.rotation_count.get(proxy.address, 0)
                if use_count >= self.usage_limit_per_ip:
                    continue  # 跳过达到使用限制的IP
                
                score = self.calculate_priority_score(proxy, domain)
                proxy_scores.append((proxy, score))
            
            if not proxy_scores:
                print("⚠️  没有满足条件的可用代理")
                return None
            
            # 选择得分最高的代理
            proxy_scores.sort(key=lambda x: x[1], reverse=True)
            selected_proxy = proxy_scores[0][0]
            
            # 更新使用记录
            self.last_rotation_time[selected_proxy.address] = current_time
            self.rotation_count[selected_proxy.address] = self.rotation_count.get(selected_proxy.address, 0) + 1
            self.last_use_time[selected_proxy.address] = current_time
            
            print(f"✅ 选择代理: {selected_proxy.address} | 评分: {proxy_scores[0][1]:.3f} | 质量: {selected_proxy.get_quality_score():.3f}")
            return selected_proxy
    
    def mark_proxy_failure(self, proxy: ProxyIP, domain: Optional[str] = None):
        """
        标记代理使用失败
        :param proxy: 失败的代理
        :param domain: 目标域名
        """
        with self.lock:
            # 记录失败域名
            if domain:
                if proxy.address not in self.failed_domains:
                    self.failed_domains[proxy.address] = []
                if domain not in self.failed_domains[proxy.address]:
                    self.failed_domains[proxy.address].append(domain)
            
            # 更新最后使用时间，以便下次轮换时考虑冷却
            self.last_use_time[proxy.address] = time.time()
            
            print(f"❌ 标记代理失败: {proxy.address}")
    
    def mark_proxy_success(self, proxy: ProxyIP):
        """
        标记代理使用成功
        :param proxy: 成功的代理
        """
        with self.lock:
            # 如果该IP在该域名上有失败记录，清除之
            if proxy.address in self.failed_domains:
                # 不清除整个列表，只保留其他域名的失败记录
                pass
            
            print(f"✅ 标记代理成功: {proxy.address}")
    
    def get_usage_statistics(self) -> Dict:
        """获取使用统计信息"""
        with self.lock:
            total_requests = sum(self.rotation_count.values())
            active_proxies = [p for p in self.proxy_pool.proxies 
                             if self.rotation_count.get(p.address, 0) > 0]
            
            return {
                'total_requests_made': total_requests,
                'active_proxy_count': len(active_proxies),
                'avg_requests_per_proxy': total_requests / len(active_proxies) if active_proxies else 0,
                'rotation_count_by_proxy': self.rotation_count.copy()
            }


class RequestScheduler:
    """请求调度器，实现智能请求间隔"""
    
    def __init__(self, min_delay: float = 1.0, max_delay: float = 5.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = {}
        self.domain_request_counts = {}
        self.lock = threading.Lock()
    
    def get_delay_for_domain(self, domain: str) -> float:
        """根据域名计算延迟"""
        with self.lock:
            # 检查该域名近期请求频率
            recent_requests = self.domain_request_counts.get(domain, [])
            recent_requests = [t for t in recent_requests if time.time() - t < 60]  # 保留1分钟内的请求
            self.domain_request_counts[domain] = recent_requests
            
            # 如果近期请求过多，增加延迟
            if len(recent_requests) > 10:  # 1分钟内超过10次请求
                return self.max_delay
            elif len(recent_requests) > 5:  # 1分钟内超过5次请求
                return self.min_delay * 2
            else:
                return random.uniform(self.min_delay, self.max_delay)
    
    def schedule_request(self, domain: str):
        """调度请求，应用适当的延迟"""
        delay = self.get_delay_for_domain(domain)
        time.sleep(delay)
        
        with self.lock:
            # 记录本次请求
            self.last_request_time[domain] = time.time()
            if domain not in self.domain_request_counts:
                self.domain_request_counts[domain] = []
            self.domain_request_counts[domain].append(time.time())


class AdvancedProxyManager:
    """高级代理管理器，整合轮换和调度功能"""
    
    def __init__(self, proxy_pool: QualityBasedProxyPool):
        self.proxy_pool = proxy_pool
        self.rotator = AdaptiveProxyRotator(
            proxy_pool=proxy_pool,
            min_interval=3,
            max_interval=20,
            usage_limit_per_ip=20,
            cool_down_period=120
        )
        self.scheduler = RequestScheduler(min_delay=1.0, max_delay=4.0)
        self.stats = {
            'successful_requests': 0,
            'failed_requests': 0,
            'rotated_proxies': 0
        }
        self.lock = threading.Lock()
    
    def make_request_with_proxy(self, request_func, domain: str, *args, **kwargs):
        """
        使用代理发送请求
        :param request_func: 请求函数
        :param domain: 目标域名
        :param args: 请求函数的位置参数
        :param kwargs: 请求函数的关键字参数
        :return: 请求结果
        """
        # 获取代理
        proxy = self.rotator.get_proxy(domain)
        if not proxy:
            print("❌ 无法获取可用代理，使用直连")
            return request_func(*args, **kwargs)
        
        # 应用请求调度延迟
        self.scheduler.schedule_request(domain)
        
        try:
            # 在请求中使用代理
            if 'proxies' not in kwargs:
                kwargs['proxies'] = {}
            kwargs['proxies'].update({
                'http': proxy.address,
                'https': proxy.address.replace('http', 'https') if proxy.protocol == 'http' else proxy.address
            })
            
            print(f"🚀 使用代理 {proxy.address} 请求 {domain}")
            result = request_func(*args, **kwargs)
            
            # 标记成功
            self.rotator.mark_proxy_success(proxy)
            with self.lock:
                self.stats['successful_requests'] += 1
            
            return result
            
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            # 标记代理失败
            self.rotator.mark_proxy_failure(proxy, domain)
            with self.lock:
                self.stats['failed_requests'] += 1
            
            raise
    
    def get_manager_stats(self) -> Dict:
        """获取管理器统计信息"""
        rotator_stats = self.rotator.get_usage_statistics()
        with self.lock:
            return {
                **self.stats,
                **rotator_stats,
                'success_rate': self.stats['successful_requests'] / 
                               (self.stats['successful_requests'] + self.stats['failed_requests']) 
                               if (self.stats['successful_requests'] + self.stats['failed_requests']) > 0 
                               else 0
            }


def demo_adaptive_rotator():
    """演示自适应轮换器"""
    print("="*60)
    print("演示: 自适应代理轮换器")
    print("="*60)
    
    # 创建代理池
    from .ip_quality_assessment import QualityBasedProxyPool, ProxyIP
    
    pool = QualityBasedProxyPool(min_quality_score=0.3)
    
    # 添加一些示例代理
    sample_proxies = [
        ProxyIP("127.0.0.1", 8080, "http"),
        ProxyIP("192.168.1.10", 8080, "http"),
        ProxyIP("proxy.example.com", 3128, "http"),
    ]
    
    # 模拟这些IP的质量评分
    for i, proxy in enumerate(sample_proxies):
        # 设置不同的质量评分
        proxy.metrics.success_rate = 0.8 - i * 0.1
        proxy.metrics.latency = 200 + i * 100
        pool.add_proxy(proxy)
    
    # 创建轮换器
    rotator = AdaptiveProxyRotator(pool)
    
    print("\n--- 获取代理测试 ---")
    for i in range(5):
        proxy = rotator.get_proxy("example.com")
        if proxy:
            print(f"第{i+1}次获取: {proxy.address}")
        else:
            print(f"第{i+1}次获取: 无可用代理")
    
    print("\n--- 使用统计 ---")
    stats = rotator.get_usage_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n演示完成")


if __name__ == "__main__":
    demo_adaptive_rotator()