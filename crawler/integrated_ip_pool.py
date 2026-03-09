"""
集成IP池系统
整合质量评估、智能轮换、监控管理等功能
"""
import time
import threading
import requests
import random
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse
from .ip_quality_assessment import QualityBasedProxyPool, ProxyIP, IPQualityMetrics
from .adaptive_proxy_rotator import AdvancedProxyManager
from .proxy_monitor import ProxyPoolManager
# 删除对Config的导入，因为我们使用自己的配置结构


class IntegratedIPPool:
    """集成IP池系统"""
    
    def __init__(self, config: Optional[Dict] = None):
        # 配置初始化
        self.config = config or {
            'min_quality_score': 0.3,
            'validation_interval': 3600,  # 1小时
            'monitoring_interval': 60,    # 1分钟
            'max_proxy_per_domain': 5,    # 每个域名最大使用代理数
            'request_delay_range': (1, 5), # 请求延迟范围(秒)
            'retry_attempts': 3,          # 重试次数
            'auto_expand_enabled': True,  # 自动扩展IP池
            'expansion_threshold': 10     # IP池低于此数量时自动扩展
        }
        
        # 初始化各组件
        self.proxy_pool = QualityBasedProxyPool(min_quality_score=self.config['min_quality_score'])
        self.advanced_manager = AdvancedProxyManager(self.proxy_pool)
        self.pool_manager = ProxyPoolManager(self.proxy_pool)
        
        # 管理后台线程
        self.shutdown_event = threading.Event()
        
        # 启动监控
        self.proxy_pool_monitor = self.pool_manager.monitor
        self.proxy_pool_monitor.start_monitoring(interval=self.config['monitoring_interval'])
        
        # 启动自动验证
        if self.config['auto_expand_enabled']:
            self.pool_manager.enable_auto_validation(interval=self.config['validation_interval'])
        
        # 记录使用情况
        self.domain_proxy_usage: Dict[str, List[str]] = {}
        self.request_history: List[Dict] = []
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_proxy_rotations': 0
        }
        
        # 锁
        self.lock = threading.Lock()
        
        print("🚀 集成IP池系统已启动")
    
    def add_proxy(self, ip: str, port: int, protocol: str = "http"):
        """添加代理IP"""
        proxy = ProxyIP(ip, port, protocol)
        self.proxy_pool.add_proxy(proxy)
        print(f"✅ 添加代理: {proxy.address}")
    
    def add_proxy_batch(self, proxy_list: List[tuple]):
        """批量添加代理IP
        proxy_list: [(ip, port, protocol), ...]
        """
        added_count = 0
        for item in proxy_list:
            if len(item) >= 2:
                ip, port = item[0], item[1]
                protocol = item[2] if len(item) >= 3 else "http"
                self.add_proxy(ip, port, protocol)
                added_count += 1
        print(f"✅ 批量添加 {added_count} 个代理")
    
    def make_request(self, url: str, method: str = "GET", **kwargs) -> requests.Response:
        """使用IP池发送请求"""
        domain = urlparse(url).netloc
        attempt = 0
        
        while attempt < self.config['retry_attempts']:
            try:
                # 获取可用代理
                proxy = self.advanced_manager.rotator.get_proxy(domain)
                
                if proxy:
                    # 记录代理使用情况
                    with self.lock:
                        if domain not in self.domain_proxy_usage:
                            self.domain_proxy_usage[domain] = []
                        if proxy.address not in self.domain_proxy_usage[domain]:
                            self.domain_proxy_usage[domain].append(proxy.address)
                        
                        # 限制每个域名使用的代理数
                        if len(self.domain_proxy_usage[domain]) > self.config['max_proxy_per_domain']:
                            # 移除使用最早的代理
                            self.domain_proxy_usage[domain].pop(0)
                
                # 发送请求
                response = self.advanced_manager.make_request_with_proxy(
                    requests.request,
                    domain,
                    method,
                    url,
                    **kwargs
                )
                
                # 更新统计
                with self.lock:
                    self.stats['total_requests'] += 1
                    self.stats['successful_requests'] += 1
                    
                    # 记录请求历史
                    self.request_history.append({
                        'timestamp': time.time(),
                        'url': url,
                        'method': method,
                        'status_code': response.status_code,
                        'proxy_used': proxy.address if proxy else 'DIRECT',
                        'success': True
                    })
                
                print(f"✅ 请求成功: {url} | 状态码: {response.status_code}")
                return response
                
            except Exception as e:
                attempt += 1
                print(f"❌ 请求失败 (尝试 {attempt}/{self.config['retry_attempts']}): {str(e)}")
                
                if attempt >= self.config['retry_attempts']:
                    # 更新失败统计
                    with self.lock:
                        self.stats['total_requests'] += 1
                        self.stats['failed_requests'] += 1
                        
                        # 记录失败请求
                        self.request_history.append({
                            'timestamp': time.time(),
                            'url': url,
                            'method': method,
                            'error': str(e),
                            'proxy_used': proxy.address if 'proxy' in locals() and proxy else 'DIRECT',
                            'success': False
                        })
                    
                    raise e
                
                # 重试前稍作延迟
                time.sleep(random.uniform(1, 3))
    
    def auto_expand_if_needed(self):
        """根据需要自动扩展IP池"""
        if not self.config['auto_expand_enabled']:
            return
            
        current_count = len(self.proxy_pool.proxies)
        if current_count < self.config['expansion_threshold']:
            print(f"🔍 IP池数量({current_count})低于阈值({self.config['expansion_threshold']})，开始自动扩展...")
            self._fetch_additional_proxies()
    
    def _fetch_additional_proxies(self):
        """获取额外的代理IP"""
        # 这里可以实现从多个来源获取IP的逻辑
        # 示例：从公共代理API获取
        sources = [
            self._fetch_from_public_api,
            self._fetch_from_free_proxies,
        ]
        
        new_proxies = []
        for source in sources:
            try:
                proxies = source()
                new_proxies.extend(proxies)
            except Exception as e:
                print(f"从{source.__name__}获取IP失败: {str(e)}")
        
        # 验证新IP
        valid_proxies = self.proxy_pool.quality_assessor.batch_validate(new_proxies)
        
        # 添加到IP池
        for proxy in valid_proxies:
            self.proxy_pool.add_proxy(proxy)
        
        print(f"✅ 自动扩展添加了 {len(valid_proxies)} 个新IP")
    
    def _fetch_from_public_api(self) -> List[ProxyIP]:
        """从公共API获取代理（示例）"""
        # 注意：实际使用时应替换为真实的代理API
        print("🔍 尝试从公共API获取代理...")
        return []
    
    def _fetch_from_free_proxies(self) -> List[ProxyIP]:
        """从免费代理源获取（示例）"""
        # 这里可以实现从免费代理网站抓取IP的逻辑
        print("🔍 尝试从免费代理源获取代理...")
        return []
    
    def get_status(self) -> Dict[str, Any]:
        """获取IP池状态"""
        pool_status = self.proxy_pool_monitor.get_current_status()
        
        with self.lock:
            overall_stats = {
                **self.stats,
                'success_rate': self.stats['successful_requests'] / self.stats['total_requests'] if self.stats['total_requests'] > 0 else 0,
                'active_domains': list(self.domain_proxy_usage.keys()),
                'recent_requests_count': len(self.request_history[-10:])  # 最近10个请求
            }
        
        return {
            'pool_status': pool_status,
            'overall_stats': overall_stats,
            'recommendations': self.pool_manager.get_recommendations()
        }
    
    def generate_full_report(self) -> str:
        """生成完整报告"""
        # 获取监控报告
        monitor_report = self.proxy_pool_monitor.generate_report()
        
        # 获取管理器详细报告
        manager_report = self.pool_manager.get_detailed_report()
        
        # 合并报告
        full_report = f"""
=== 集成IP池系统完整报告 ===
生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

{manager_report}

=== 监控报告摘要 ===
{monitor_report}

=== 系统统计 ===
总请求数: {self.stats['total_requests']}
成功请求数: {self.stats['successful_requests']}
失败请求数: {self.stats['failed_requests']}
成功率: {self.stats['successful_requests']/self.stats['total_requests']*100:.2f% if self.stats['total_requests'] > 0 else 0}%

使用过的域名: {list(self.domain_proxy_usage.keys())}
        """
        
        return full_report
    
    def cleanup_old_requests(self, hours: int = 24):
        """清理旧的请求记录"""
        cutoff_time = time.time() - (hours * 3600)
        
        with self.lock:
            self.request_history = [
                req for req in self.request_history 
                if req['timestamp'] > cutoff_time
            ]
        
        print(f"🗑️ 清理了 {hours} 小时前的请求记录")
    
    def shutdown(self):
        """关闭IP池系统，停止所有后台线程"""
        print("🛑 正在关闭集成IP池系统...")
        
        # 停止监控
        self.proxy_pool_monitor.stop_monitoring()
        
        # 停止自动验证
        self.pool_manager.disable_auto_validation()
        
        print("✅ 集成IP池系统已关闭")


def create_optimized_proxy_session(integrated_pool: IntegratedIPPool):
    """创建优化的代理会话"""
    class OptimizedProxySession(requests.Session):
        def __init__(self, integrated_pool):
            super().__init__()
            self.integrated_pool = integrated_pool
        
        def request(self, method, url, **kwargs):
            return self.integrated_pool.make_request(url, method, **kwargs)
    
    return OptimizedProxySession(integrated_pool)


def demo_integrated_ip_pool():
    """演示集成IP池系统"""
    print("="*60)
    print("演示: 集成IP池系统")
    print("="*60)
    
    # 创建集成IP池
    config = {
        'min_quality_score': 0.3,
        'validation_interval': 7200,  # 2小时
        'monitoring_interval': 30,    # 30秒
        'max_proxy_per_domain': 3,
        'request_delay_range': (1, 3),
        'retry_attempts': 2,
        'auto_expand_enabled': False,  # 演示时不自动扩展
        'expansion_threshold': 5
    }
    
    pool = IntegratedIPPool(config)
    
    # 添加一些示例代理
    sample_proxies = [
        ("127.0.0.1", 8080, "http"),
        ("192.168.1.10", 8080, "http"),
        ("proxy.example.com", 3128, "http"),
    ]
    
    pool.add_proxy_batch(sample_proxies)
    
    # 获取状态
    status = pool.get_status()
    print(f"\n--- 当前状态 ---")
    print(f"IP池状态: {status['pool_status']}")
    print(f"整体统计: {status['overall_stats']}")
    print(f"建议: {status['recommendations']}")
    
    # 模拟一些请求
    print(f"\n--- 模拟请求 ---")
    try:
        # 使用优化的会话
        session = create_optimized_proxy_session(pool)
        
        # 这里我们不实际发出请求，仅演示如何使用
        print("💡 演示如何使用集成IP池发送请求:")
        print("# session = create_optimized_proxy_session(pool)")
        print("# response = session.get('https://example.com')")
        print("# print(f'状态码: {response.status_code}')")
        
    except Exception as e:
        print(f"演示请求过程中出错: {str(e)}")
    
    # 生成完整报告
    print(f"\n--- 生成完整报告 ---")
    report = pool.generate_full_report()
    print(report[:500] + "...")  # 只打印前500个字符
    
    print(f"\n✅ 演示完成")


if __name__ == "__main__":
    demo_integrated_ip_pool()