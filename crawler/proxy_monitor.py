"""
IP池监控与管理系统
提供实时监控、统计分析和可视化功能
"""
import time
import threading
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
from .ip_quality_assessment import QualityBasedProxyPool, ProxyIP
from .adaptive_proxy_rotator import AdvancedProxyManager


@dataclass
class MonitoringMetrics:
    """监控指标"""
    timestamp: datetime
    total_proxies: int
    active_proxies: int
    high_quality_proxies: int
    avg_success_rate: float
    avg_latency: float
    successful_requests: int
    failed_requests: int
    success_rate: float
    unique_ips_used: int


class ProxyPoolMonitor:
    """IP池监控器"""
    
    def __init__(self, proxy_pool: QualityBasedProxyPool, manager: Optional[AdvancedProxyManager] = None):
        self.proxy_pool = proxy_pool
        self.manager = manager
        self.metrics_history: List[MonitoringMetrics] = []
        self.monitoring_thread: Optional[threading.Thread] = None
        self.is_monitoring = False
        self.update_interval = 60  # 更新间隔(秒)
        self.data_lock = threading.Lock()
        
    def start_monitoring(self, interval: int = 60):
        """开始监控IP池"""
        self.update_interval = interval
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitoring_thread.start()
        print(f"📊 开始监控IP池，更新间隔: {interval}秒")
        
    def stop_monitoring(self):
        """停止监控IP池"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        print("📊 停止监控IP池")
        
    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                self._collect_metrics()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"❌ 监控循环出错: {str(e)}")
                time.sleep(self.update_interval)
                
    def _collect_metrics(self):
        """收集当前指标"""
        stats = self.proxy_pool.get_statistics()
        
        # 如果有管理器，获取更多统计信息
        manager_stats = {}
        if self.manager:
            manager_stats = self.manager.get_manager_stats()
        
        with self.data_lock:
            metrics = MonitoringMetrics(
                timestamp=datetime.now(),
                total_proxies=stats['total_proxies'],
                active_proxies=stats['high_quality_proxies'],  # 将高质代理视为活跃代理
                high_quality_proxies=stats['high_quality_proxies'],
                avg_success_rate=stats['average_success_rate'],
                avg_latency=stats['average_latency'],
                successful_requests=manager_stats.get('successful_requests', 0),
                failed_requests=manager_stats.get('failed_requests', 0),
                success_rate=manager_stats.get('success_rate', 0),
                unique_ips_used=manager_stats.get('active_proxy_count', 0)
            )
            
            self.metrics_history.append(metrics)
            
            # 只保留最近24小时的数据
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.metrics_history = [m for m in self.metrics_history if m.timestamp > cutoff_time]
        
        # 打印当前指标
        print(f"[{metrics.timestamp.strftime('%H:%M:%S')}] "
              f"IP池: 总IP={metrics.total_proxies}, 高质IP={metrics.active_proxies}, "
              f"成功率={metrics.success_rate:.2%}, 平均延迟={metrics.avg_latency:.2f}ms, "
              f"成功请求={metrics.successful_requests}, 失败请求={metrics.failed_requests}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        if not self.metrics_history:
            return {"error": "暂无监控数据"}
            
        latest = self.metrics_history[-1]
        return {
            "timestamp": latest.timestamp.isoformat(),
            "total_proxies": latest.total_proxies,
            "high_quality_proxies": latest.high_quality_proxies,
            "avg_success_rate": latest.avg_success_rate,
            "avg_latency": latest.avg_latency,
            "successful_requests": latest.successful_requests,
            "failed_requests": latest.failed_requests,
            "request_success_rate": latest.success_rate,
            "unique_ips_used": latest.unique_ips_used,
            "health_percentage": latest.high_quality_proxies / latest.total_proxies * 100 if latest.total_proxies > 0 else 0
        }
    
    def generate_report(self, save_path: Optional[str] = None) -> str:
        """生成监控报告"""
        if not self.metrics_history:
            return "暂无监控数据可生成报告"
        
        try:
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
        except ImportError:
            # 如果没有matplotlib，生成纯文本报告
            return self._generate_text_only_report()
        
        # 准备绘图数据
        timestamps = [m.timestamp for m in self.metrics_history]
        total_proxies = [m.total_proxies for m in self.metrics_history]
        active_proxies = [m.active_proxies for m in self.metrics_history]
        success_rates = [m.success_rate for m in self.metrics_history]
        avg_latencies = [m.avg_latency for m in self.metrics_history]
        success_requests = [m.successful_requests for m in self.metrics_history]
        fail_requests = [m.failed_requests for m in self.metrics_history]
        
        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('IP池监控报告', fontsize=16)
        
        # IP数量趋势图
        ax1 = axes[0, 0]
        ax1.plot(timestamps, total_proxies, label='总IP数', marker='o')
        ax1.plot(timestamps, active_proxies, label='高质IP数', marker='s')
        ax1.set_title('IP池数量变化')
        ax1.set_xlabel('时间')
        ax1.set_ylabel('IP数量')
        ax1.legend()
        ax1.grid(True)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d\n%H:%M'))
        
        # 成功率趋势图
        ax2 = axes[0, 1]
        ax2.plot(timestamps, success_rates, label='请求成功率', color='green', marker='o')
        ax2.set_title('请求成功率变化')
        ax2.set_xlabel('时间')
        ax2.set_ylabel('成功率')
        ax2.legend()
        ax2.grid(True)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d\n%H:%M'))
        
        # 延迟趋势图
        ax3 = axes[1, 0]
        ax3.plot(timestamps, avg_latencies, label='平均延迟', color='orange', marker='^')
        ax3.set_title('平均响应延迟变化')
        ax3.set_xlabel('时间')
        ax3.set_ylabel('延迟(ms)')
        ax3.legend()
        ax3.grid(True)
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d\n%H:%M'))
        
        # 请求统计图
        ax4 = axes[1, 1]
        width = 0.35
        x = range(len(timestamps))
        ax4.bar([i - width/2 for i in x], success_requests, width, label='成功请求', alpha=0.7)
        ax4.bar([i + width/2 for i in x], fail_requests, width, label='失败请求', alpha=0.7)
        ax4.set_title('请求统计')
        ax4.set_xlabel('时间点')
        ax4.set_ylabel('请求数')
        ax4.legend()
        ax4.grid(True, axis='y')
        
        plt.tight_layout()
        
        # 保存图表
        if save_path is None:
            save_path = f'proxy_pool_monitor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # 生成文本报告
        latest = self.metrics_history[-1]
        text_report = f"""
IP池监控报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
监测期间: {self.metrics_history[0].timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {latest.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

=== IP池状态 ===
总IP数量: {latest.total_proxies}
高质IP数量: {latest.high_quality_proxies}
IP池健康度: {latest.high_quality_proxies/latest.total_proxies*100:.2f}% 

=== 性能指标 ===
平均成功率: {latest.avg_success_rate:.2%}
平均延迟: {latest.avg_latency:.2f}ms
总体请求成功率: {latest.success_rate:.2%}

=== 请求统计 ===
成功请求数: {latest.successful_requests}
失败请求数: {latest.failed_requests}
使用独立IP数: {latest.unique_ips_used}

图表已保存至: {save_path}
        """
        
        return text_report

    def _generate_text_only_report(self) -> str:
        """生成纯文本报告（当matplotlib不可用时）"""
        if not self.metrics_history:
            return "暂无监控数据可生成报告"
        
        latest = self.metrics_history[-1]
        text_report = f"""
IP池监控报告 (纯文本版)
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
监测期间: {self.metrics_history[0].timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {latest.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

=== IP池状态 ===
总IP数量: {latest.total_proxies}
高质IP数量: {latest.high_quality_proxies}
IP池健康度: {latest.high_quality_proxies/latest.total_proxies*100:.2f}% 

=== 性能指标 ===
平均成功率: {latest.avg_success_rate:.2%}
平均延迟: {latest.avg_latency:.2f}ms
总体请求成功率: {latest.success_rate:.2%}

=== 请求统计 ===
成功请求数: {latest.successful_requests}
失败请求数: {latest.failed_requests}
使用独立IP数: {latest.unique_ips_used}

注意: matplotlib未安装，无法生成可视化图表
        """
        
        return text_report
    
    def export_data(self, filepath: str):
        """导出监控数据到JSON文件"""
        data = []
        for metric in self.metrics_history:
            data.append({
                "timestamp": metric.timestamp.isoformat(),
                "total_proxies": metric.total_proxies,
                "active_proxies": metric.active_proxies,
                "high_quality_proxies": metric.high_quality_proxies,
                "avg_success_rate": metric.avg_success_rate,
                "avg_latency": metric.avg_latency,
                "successful_requests": metric.successful_requests,
                "failed_requests": metric.failed_requests,
                "success_rate": metric.success_rate,
                "unique_ips_used": metric.unique_ips_used
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"📊 监控数据已导出至: {filepath}")


class ProxyPoolManager:
    """IP池综合管理器"""
    
    def __init__(self, proxy_pool: QualityBasedProxyPool):
        self.proxy_pool = proxy_pool
        self.monitor = ProxyPoolMonitor(proxy_pool)
        self.auto_validation_enabled = False
        self.validation_thread = None
        self.validation_interval = 3600  # 1小时验证一次
    
    def enable_auto_validation(self, interval: int = 3600):
        """启用自动验证"""
        self.validation_interval = interval
        self.auto_validation_enabled = True
        self.validation_thread = threading.Thread(target=self._validation_loop, daemon=True)
        self.validation_thread.start()
        print(f"✅ 启用自动验证，间隔: {interval}秒")
    
    def disable_auto_validation(self):
        """禁用自动验证"""
        self.auto_validation_enabled = False
        print("✅ 已禁用自动验证")
    
    def _validation_loop(self):
        """验证循环"""
        while self.auto_validation_enabled:
            try:
                print("🔄 开始自动验证代理IP...")
                self.proxy_pool.validate_all_proxies()
                time.sleep(self.validation_interval)
            except Exception as e:
                print(f"❌ 自动验证循环出错: {str(e)}")
                time.sleep(self.validation_interval)
    
    def get_recommendations(self) -> List[str]:
        """获取优化建议"""
        recommendations = []
        stats = self.proxy_pool.get_statistics()
        
        # 检查IP池健康度
        health = stats['health_percentage']
        if health < 50:
            recommendations.append("⚠️ IP池健康度过低 (<50%)，建议增加高质量IP来源")
        elif health < 80:
            recommendations.append("⚠️ IP池健康度一般 (<80%)，可考虑优化IP质量")
        
        # 检查平均延迟
        if stats['average_latency'] > 2000:  # 2秒以上
            recommendations.append("⚠️ 平均延迟过高 (>2秒)，建议筛选低延迟IP")
        
        # 检查成功率
        if stats['average_success_rate'] < 0.7:  # 70%以下
            recommendations.append("⚠️ 平均成功率低 (<70%)，需要提升IP质量")
        
        # 如果IP池太小
        if stats['total_proxies'] < 10:
            recommendations.append("💡 IP池规模较小，建议扩充IP来源")
        
        # 如果没有建议
        if not recommendations:
            recommendations.append("✅ IP池状态良好，继续保持")
        
        return recommendations
    
    def get_detailed_report(self) -> str:
        """获取详细报告"""
        stats = self.proxy_pool.get_statistics()
        recommendations = self.get_recommendations()
        
        # 获取质量分布
        quality_ranges = {
            "优秀 (>0.8)": 0,
            "良好 (0.6-0.8)": 0,
            "一般 (0.4-0.6)": 0,
            "较差 (<0.4)": 0
        }
        
        for proxy in self.proxy_pool.proxies:
            score = proxy.get_quality_score()
            if score > 0.8:
                quality_ranges["优秀 (>0.8)"] += 1
            elif score > 0.6:
                quality_ranges["良好 (0.6-0.8)"] += 1
            elif score > 0.4:
                quality_ranges["一般 (0.4-0.6)"] += 1
            else:
                quality_ranges["较差 (<0.4)"] += 1
        
        report = f"""
=== IP池详细报告 ===
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 基本统计:
总IP数量: {stats['total_proxies']}
高质IP数量: {stats['high_quality_proxies']}
平均成功率: {stats['average_success_rate']:.2%}
平均延迟: {stats['average_latency']:.2f}ms
IP池健康度: {stats['health_percentage']:.2f}%

📈 质量分布:
"""
        for range_name, count in quality_ranges.items():
            report += f"- {range_name}: {count} 个\n"
        
        report += f"""
💡 优化建议:
"""
        for rec in recommendations:
            report += f"- {rec}\n"
        
        return report


def demo_proxy_monitor():
    """演示监控系统"""
    print("="*60)
    print("演示: IP池监控系统")
    print("="*60)
    
    # 创建代理池
    from .ip_quality_assessment import QualityBasedProxyPool, ProxyIP
    
    pool = QualityBasedProxyPool(min_quality_score=0.3)
    
    # 添加一些示例代理
    for i in range(5):
        proxy = ProxyIP(f"192.168.1.{i+1}", 8080, "http")
        # 设置不同的质量评分
        proxy.metrics.success_rate = 0.8 - i * 0.1
        proxy.metrics.latency = 200 + i * 100
        pool.add_proxy(proxy)
    
    # 创建监控器
    monitor = ProxyPoolMonitor(pool)
    
    # 模拟一些监控数据
    for i in range(3):
        monitor._collect_metrics()
        time.sleep(0.1)  # 快速模拟数据收集
    
    # 获取当前状态
    status = monitor.get_current_status()
    print("\n--- 当前状态 ---")
    for key, value in status.items():
        print(f"{key}: {value}")
    
    # 创建管理器
    manager = ProxyPoolManager(pool)
    
    # 获取详细报告
    report = manager.get_detailed_report()
    print(f"\n--- 详细报告 ---\n{report}")
    
    # 获取优化建议
    recommendations = manager.get_recommendations()
    print("--- 优化建议 ---")
    for rec in recommendations:
        print(rec)
    
    print("\n演示完成")


if __name__ == "__main__":
    demo_proxy_monitor()