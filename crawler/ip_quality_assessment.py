"""
IP质量评估模块
用于评估和管理代理IP的质量
"""
import time
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import requests
import random


@dataclass
class IPQualityMetrics:
    """IP质量指标"""
    success_rate: float = 0.0  # 请求成功率
    latency: float = float('inf')  # 响应延迟
    anonymity_level: int = 0  # 匿名级别(0-高匿名,1-普通匿名,2-透明)
    stability: float = 0.0  # 稳定性评分
    last_test_time: Optional[datetime] = None
    test_count: int = 0
    success_count: int = 0
    region: str = ""  # 地区信息
    isp: str = ""  # ISP信息
    
    def update_metrics(self, success: bool, latency: float = float('inf'), region: str = "", isp: str = ""):
        """更新质量指标"""
        self.test_count += 1
        if success:
            self.success_count += 1
        
        # 使用指数加权移动平均更新成功率
        alpha = 0.2
        self.success_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * self.success_rate
        
        # 更新延迟（使用EMA）
        if latency > 0 and latency != float('inf'):
            if self.latency == float('inf'):
                self.latency = latency
            else:
                self.latency = alpha * latency + (1 - alpha) * self.latency
        
        # 更新地区和ISP信息
        if region:
            self.region = region
        if isp:
            self.isp = isp
            
        self.last_test_time = datetime.now()


class ProxyIP:
    """代理IP类"""
    def __init__(self, ip: str, port: int, protocol: str = "http"):
        self.ip = ip
        self.port = port
        self.protocol = protocol
        self.address = f"{protocol}://{ip}:{port}"
        self.metrics = IPQualityMetrics()
        self.status = "active"  # active, inactive, banned
        self.created_at = datetime.now()
        self.last_used = None
        
    def get_quality_score(self) -> float:
        """获取质量评分"""
        # 综合评分：成功率权重0.5，延迟权重0.3，稳定性权重0.2
        # 延迟评分：越低越好，转换为0-1区间
        latency_score = 0.0
        if self.metrics.latency != float('inf'):
            # 假设最大延迟为5秒，转换为0-1评分
            latency_score = max(0, 1 - self.metrics.latency / 5000)
        
        score = (
            self.metrics.success_rate * 0.5 +
            latency_score * 0.3 +
            self.metrics.stability * 0.2
        )
        
        # 如果长时间未测试，降低分数
        if self.metrics.last_test_time:
            hours_since_test = (datetime.now() - self.metrics.last_test_time).total_seconds() / 3600
            if hours_since_test > 24:  # 超过24小时未测试
                score *= 0.8  # 降低20%
        
        return score
    
    def update_usage_stats(self):
        """更新使用统计"""
        self.last_used = datetime.now()


class IPQualityAssessor:
    """IP质量评估器"""
    def __init__(self, test_urls: Optional[List[str]] = None):
        self.test_urls = test_urls or ["http://httpbin.org/ip", "https://httpbin.org/user-agent"]
        self.validation_timeout = 10
        self.test_threads = 10
        
    def validate_proxy(self, proxy: ProxyIP) -> tuple[bool, float]:
        """
        验证代理IP的有效性
        返回: (是否有效, 响应时间毫秒)
        """
        proxies = {
            'http': proxy.address,
            'https': proxy.address
        }
        
        start_time = time.time()
        try:
            # 测试连接
            response = requests.get(
                random.choice(self.test_urls),
                proxies=proxies,
                timeout=self.validation_timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; IPValidator/1.0)'
                }
            )
            
            latency = (time.time() - start_time) * 1000
            is_valid = response.status_code == 200
            
            # 尝试获取IP地理位置信息（如果可用）
            if is_valid:
                try:
                    # 使用免费的IP地理位置API
                    geo_response = requests.get(
                        f"http://ip-api.com/json/{proxy.ip}?fields=status,message,country,regionName,isp",
                        timeout=5
                    )
                    if geo_response.status_code == 200:
                        geo_data = geo_response.json()
                        if geo_data.get('status') == 'success':
                            region = f"{geo_data.get('country', '')}-{geo_data.get('regionName', '')}"
                            isp = geo_data.get('isp', '')
                            proxy.metrics.region = region
                            proxy.metrics.isp = isp
                except:
                    pass  # 忽略地理位置查询错误
                    
            return is_valid, latency
            
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            print(f"验证代理 {proxy.address} 时出错: {str(e)}")
            return False, latency
    
    def batch_validate(self, proxies: List[ProxyIP]) -> List[ProxyIP]:
        """批量验证代理IP"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        valid_proxies = []
        
        with ThreadPoolExecutor(max_workers=self.test_threads) as executor:
            # 提交所有验证任务
            future_to_proxy = {
                executor.submit(self.validate_proxy, proxy): proxy 
                for proxy in proxies
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    is_valid, latency = future.result()
                    
                    if is_valid:
                        proxy.metrics.update_metrics(True, latency)
                        valid_proxies.append(proxy)
                        print(f"✅ 有效代理: {proxy.address} | 延迟: {latency:.2f}ms | 评分: {proxy.get_quality_score():.2f}")
                    else:
                        proxy.metrics.update_metrics(False)
                        print(f"❌ 无效代理: {proxy.address}")
                        
                except Exception as e:
                    print(f"❌ 验证 {proxy.address} 时出错: {str(e)}")
                    proxy.metrics.update_metrics(False)
        
        return valid_proxies


class QualityBasedProxyPool:
    """基于质量的代理池"""
    def __init__(self, min_quality_score: float = 0.5):
        self.proxies: List[ProxyIP] = []
        self.quality_assessor = IPQualityAssessor()
        self.min_quality_score = min_quality_score
        self.lock = threading.Lock()
        
    def add_proxy(self, proxy: ProxyIP):
        """添加代理到池中"""
        with self.lock:
            # 检查是否已存在相同IP和端口的代理
            for existing_proxy in self.proxies:
                if existing_proxy.ip == proxy.ip and existing_proxy.port == proxy.port:
                    print(f"代理 {proxy.address} 已存在，跳过添加")
                    return
            
            self.proxies.append(proxy)
            print(f"已添加代理: {proxy.address}")
    
    def remove_proxy(self, proxy: ProxyIP):
        """从池中移除代理"""
        with self.lock:
            if proxy in self.proxies:
                self.proxies.remove(proxy)
                print(f"已移除代理: {proxy.address}")
    
    def get_high_quality_proxies(self, min_score: Optional[float] = None) -> List[ProxyIP]:
        """获取高质量代理列表"""
        threshold = min_score or self.min_quality_score
        with self.lock:
            return [p for p in self.proxies if p.get_quality_score() >= threshold]
    
    def get_best_proxy(self) -> Optional[ProxyIP]:
        """获取质量最好的代理"""
        high_quality = self.get_high_quality_proxies()
        if high_quality:
            return max(high_quality, key=lambda p: p.get_quality_score())
        return None
    
    def get_random_proxy(self) -> Optional[ProxyIP]:
        """随机获取一个高质量代理"""
        high_quality = self.get_high_quality_proxies()
        if high_quality:
            return random.choice(high_quality)
        return None
    
    def validate_all_proxies(self):
        """验证池中所有代理"""
        print(f"开始验证 {len(self.proxies)} 个代理...")
        valid_proxies = self.quality_assessor.batch_validate(self.proxies)
        
        # 移除无效代理
        with self.lock:
            invalid_proxies = [p for p in self.proxies if p not in valid_proxies]
            for proxy in invalid_proxies:
                self.proxies.remove(proxy)
                print(f"已移除无效代理: {proxy.address}")
        
        print(f"验证完成，剩余 {len(self.proxies)} 个有效代理")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取代理池统计信息"""
        with self.lock:
            total = len(self.proxies)
            high_quality = len(self.get_high_quality_proxies())
            avg_latency = 0
            avg_success_rate = 0
            
            if total > 0:
                valid_latencies = [p.metrics.latency for p in self.proxies if p.metrics.latency != float('inf')]
                if valid_latencies:
                    avg_latency = sum(valid_latencies) / len(valid_latencies)
                
                avg_success_rate = sum(p.metrics.success_rate for p in self.proxies) / total
            
            return {
                'total_proxies': total,
                'high_quality_proxies': high_quality,
                'average_latency': avg_latency,
                'average_success_rate': avg_success_rate,
                'health_percentage': (high_quality / total * 100) if total > 0 else 0
            }


def demo_quality_based_proxy_pool():
    """演示基于质量的代理池"""
    print("="*60)
    print("演示: 基于质量的代理池")
    print("="*60)
    
    # 创建代理池
    pool = QualityBasedProxyPool(min_quality_score=0.3)
    
    # 添加一些示例代理（注意：这些是示例，实际可能不可用）
    sample_proxies = [
        ProxyIP("127.0.0.1", 8080, "http"),
        ProxyIP("192.168.1.1", 80, "http"),
        ProxyIP("proxy.example.com", 3128, "http"),
    ]
    
    for proxy in sample_proxies:
        pool.add_proxy(proxy)
    
    # 获取统计信息
    stats = pool.get_statistics()
    print(f"初始统计: {stats}")
    
    # 验证所有代理
    pool.validate_all_proxies()
    
    # 再次获取统计信息
    stats = pool.get_statistics()
    print(f"验证后统计: {stats}")
    
    # 获取最佳代理
    best_proxy = pool.get_best_proxy()
    if best_proxy:
        print(f"最佳代理: {best_proxy.address} (评分: {best_proxy.get_quality_score():.2f})")
    
    print("\n演示完成")


if __name__ == "__main__":
    demo_quality_based_proxy_pool()