"""
业务关键指标监控模块
监控系统业务关键指标，包括数据采集、用户行为、决策质量等
"""
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque
import json
import asyncio

logger = logging.getLogger(__name__)


class BusinessMetricsCollector:
    """业务指标收集器"""
    
    def __init__(self):
        self.metrics = {
            "data_collection": {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_data_points": 0,
                "last_collection_time": None,
                "collection_latency": deque(maxlen=100),  # 最近100次采集延迟
                "data_sources": defaultdict(lambda: {
                    "requests": 0,
                    "success": 0,
                    "failures": 0,
                    "last_success": None,
                    "last_failure": None
                })
            },
            "user_activity": {
                "total_logins": 0,
                "active_users": 0,
                "api_calls": defaultdict(int),
                "last_activity": defaultdict(lambda: None)
            },
            "decision_quality": {
                "total_decisions": 0,
                "correct_decisions": 0,
                "incorrect_decisions": 0,
                "decision_confidence": deque(maxlen=100),
                "decision_latency": deque(maxlen=100)
            },
            "system_performance": {
                "cache_hit_rate": deque(maxlen=100),
                "database_query_time": deque(maxlen=100),
                "api_response_time": deque(maxlen=100),
                "error_rate": deque(maxlen=100)
            },
            "business_value": {
                "data_quality_score": 0.0,
                "user_satisfaction_score": 0.0,
                "system_reliability_score": 0.0,
                "business_impact_score": 0.0
            }
        }
        
        # 历史数据存储（最近24小时）
        self.history = {
            "hourly": defaultdict(lambda: deque(maxlen=24)),
            "daily": defaultdict(lambda: deque(maxlen=30))
        }
        
        # 告警配置
        self.alerts_config = {
            "data_collection_failure_rate": 0.1,  # 10%失败率触发告警
            "decision_accuracy_threshold": 0.7,    # 70%准确率阈值
            "system_response_time_threshold": 2.0, # 2秒响应时间阈值
            "cache_hit_rate_threshold": 0.8,       # 80%缓存命中率阈值
            "user_activity_drop_threshold": 0.5    # 50%用户活跃度下降阈值
        }
        
        self.active_alerts = []
        
    def record_data_collection(
        self, 
        source_id: str, 
        success: bool, 
        data_points: int = 0,
        latency: float = 0.0
    ):
        """记录数据采集指标"""
        metrics = self.metrics["data_collection"]
        
        metrics["total_requests"] += 1
        metrics["total_data_points"] += data_points
        
        if success:
            metrics["successful_requests"] += 1
            metrics["data_sources"][source_id]["success"] += 1
            metrics["data_sources"][source_id]["last_success"] = datetime.now()
        else:
            metrics["failed_requests"] += 1
            metrics["data_sources"][source_id]["failures"] += 1
            metrics["data_sources"][source_id]["last_failure"] = datetime.now()
        
        metrics["data_sources"][source_id]["requests"] += 1
        metrics["last_collection_time"] = datetime.now()
        
        if latency > 0:
            metrics["collection_latency"].append(latency)
        
        # 检查是否需要触发告警
        self._check_data_collection_alerts(source_id)
        
        # 记录历史数据
        self._record_hourly_metric("data_collection_requests", 1)
        if success:
            self._record_hourly_metric("data_collection_success", 1)
        else:
            self._record_hourly_metric("data_collection_failures", 1)
    
    def record_user_activity(self, user_id: str, action: str):
        """记录用户活动指标"""
        metrics = self.metrics["user_activity"]
        
        if action == "login":
            metrics["total_logins"] += 1
        
        metrics["api_calls"][action] += 1
        metrics["last_activity"][user_id] = datetime.now()
        
        # 更新活跃用户数
        active_threshold = datetime.now() - timedelta(minutes=30)
        active_users = sum(
            1 for last_time in metrics["last_activity"].values()
            if last_time and last_time > active_threshold
        )
        metrics["active_users"] = active_users
        
        # 记录历史数据
        self._record_hourly_metric("user_activity", 1)
        self._record_hourly_metric("active_users", active_users)
    
    def record_decision(
        self, 
        decision_id: str, 
        correct: Optional[bool] = None,
        confidence: float = 0.0,
        latency: float = 0.0
    ):
        """记录决策质量指标"""
        metrics = self.metrics["decision_quality"]
        
        metrics["total_decisions"] += 1
        
        if correct is not None:
            if correct:
                metrics["correct_decisions"] += 1
            else:
                metrics["incorrect_decisions"] += 1
        
        if confidence > 0:
            metrics["decision_confidence"].append(confidence)
        
        if latency > 0:
            metrics["decision_latency"].append(latency)
        
        # 检查决策质量告警
        self._check_decision_quality_alerts()
        
        # 记录历史数据
        self._record_hourly_metric("total_decisions", 1)
        if correct:
            self._record_hourly_metric("correct_decisions", 1 if correct else 0)
    
    def record_system_performance(
        self,
        metric_type: str,
        value: float
    ):
        """记录系统性能指标"""
        if metric_type in self.metrics["system_performance"]:
            self.metrics["system_performance"][metric_type].append(value)
            
            # 检查系统性能告警
            self._check_system_performance_alerts(metric_type, value)
            
            # 记录历史数据
            self._record_hourly_metric(f"system_{metric_type}", value)
    
    def calculate_business_value_metrics(self):
        """计算业务价值指标"""
        metrics = self.metrics
        
        # 数据质量评分（基于采集成功率和数据完整性）
        data_collection = metrics["data_collection"]
        if data_collection["total_requests"] > 0:
            success_rate = data_collection["successful_requests"] / data_collection["total_requests"]
        else:
            success_rate = 0
        
        # 用户满意度评分（基于活跃度和API使用）
        user_activity = metrics["user_activity"]
        activity_score = min(user_activity["total_logins"] / 100, 1.0)  # 归一化
        
        # 系统可靠性评分（基于错误率和响应时间）
        system_perf = metrics["system_performance"]
        error_rate = self._calculate_average(system_perf["error_rate"]) if system_perf["error_rate"] else 0
        reliability_score = max(0, 1 - error_rate)
        
        # 业务影响评分（基于决策质量和数据价值）
        decision_quality = metrics["decision_quality"]
        if decision_quality["total_decisions"] > 0:
            accuracy = decision_quality["correct_decisions"] / decision_quality["total_decisions"]
        else:
            accuracy = 0
        
        # 计算综合业务价值评分
        business_value = {
            "data_quality_score": round(success_rate * 100, 2),
            "user_satisfaction_score": round(activity_score * 100, 2),
            "system_reliability_score": round(reliability_score * 100, 2),
            "business_impact_score": round(accuracy * 100, 2),
            "overall_score": round((success_rate + activity_score + reliability_score + accuracy) / 4 * 100, 2),
            "timestamp": datetime.now().isoformat()
        }
        
        metrics["business_value"].update(business_value)
        return business_value
    
    def _check_data_collection_alerts(self, source_id: str):
        """检查数据采集告警"""
        source_metrics = self.metrics["data_collection"]["data_sources"][source_id]
        
        if source_metrics["requests"] > 10:
            failure_rate = source_metrics["failures"] / source_metrics["requests"]
            
            if failure_rate > self.alerts_config["data_collection_failure_rate"]:
                alert = {
                    "type": "data_collection_failure",
                    "source_id": source_id,
                    "failure_rate": failure_rate,
                    "threshold": self.alerts_config["data_collection_failure_rate"],
                    "timestamp": datetime.now().isoformat(),
                    "severity": "high" if failure_rate > 0.3 else "medium"
                }
                
                if not self._is_alert_active(alert["type"], source_id):
                    self.active_alerts.append(alert)
                    logger.warning(f"数据采集失败告警: {source_id}, 失败率: {failure_rate:.2%}")
    
    def _check_decision_quality_alerts(self):
        """检查决策质量告警"""
        metrics = self.metrics["decision_quality"]
        
        if metrics["total_decisions"] > 20:
            accuracy = metrics["correct_decisions"] / metrics["total_decisions"]
            
            if accuracy < self.alerts_config["decision_accuracy_threshold"]:
                alert = {
                    "type": "decision_accuracy_low",
                    "accuracy": accuracy,
                    "threshold": self.alerts_config["decision_accuracy_threshold"],
                    "total_decisions": metrics["total_decisions"],
                    "timestamp": datetime.now().isoformat(),
                    "severity": "high" if accuracy < 0.5 else "medium"
                }
                
                if not self._is_alert_active(alert["type"]):
                    self.active_alerts.append(alert)
                    logger.warning(f"决策准确率低告警: {accuracy:.2%}")
    
    def _check_system_performance_alerts(self, metric_type: str, value: float):
        """检查系统性能告警"""
        if metric_type == "api_response_time":
            threshold = self.alerts_config["system_response_time_threshold"]
            if value > threshold:
                alert = {
                    "type": "high_response_time",
                    "metric": metric_type,
                    "value": value,
                    "threshold": threshold,
                    "timestamp": datetime.now().isoformat(),
                    "severity": "medium"
                }
                
                if not self._is_alert_active(alert["type"]):
                    self.active_alerts.append(alert)
                    logger.warning(f"高响应时间告警: {metric_type}={value:.2f}s")
        
        elif metric_type == "cache_hit_rate":
            threshold = self.alerts_config["cache_hit_rate_threshold"]
            if value < threshold:
                alert = {
                    "type": "low_cache_hit_rate",
                    "metric": metric_type,
                    "value": value,
                    "threshold": threshold,
                    "timestamp": datetime.now().isoformat(),
                    "severity": "low"
                }
                
                if not self._is_alert_active(alert["type"]):
                    self.active_alerts.append(alert)
                    logger.warning(f"低缓存命中率告警: {metric_type}={value:.2%}")
    
    def _is_alert_active(self, alert_type: str, identifier: str = "") -> bool:
        """检查告警是否已存在"""
        for alert in self.active_alerts:
            if alert["type"] == alert_type:
                if identifier and alert.get("source_id") == identifier:
                    return True
                elif not identifier:
                    return True
        return False
    
    def _record_hourly_metric(self, metric_name: str, value: Any):
        """记录小时级指标"""
        hour_key = datetime.now().strftime("%Y-%m-%d-%H")
        self.history["hourly"][metric_name].append({
            "timestamp": hour_key,
            "value": value
        })
    
    def _calculate_average(self, deque_obj: deque) -> float:
        """计算双端队列的平均值"""
        if not deque_obj:
            return 0.0
        return sum(deque_obj) / len(deque_obj)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "data_collection": {
                "total_requests": self.metrics["data_collection"]["total_requests"],
                "success_rate": self._calculate_success_rate("data_collection"),
                "avg_latency": self._calculate_average(self.metrics["data_collection"]["collection_latency"]),
                "active_sources": len(self.metrics["data_collection"]["data_sources"])
            },
            "user_activity": {
                "total_logins": self.metrics["user_activity"]["total_logins"],
                "active_users": self.metrics["user_activity"]["active_users"],
                "top_actions": dict(sorted(
                    self.metrics["user_activity"]["api_calls"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5])
            },
            "decision_quality": {
                "total_decisions": self.metrics["decision_quality"]["total_decisions"],
                "accuracy": self._calculate_accuracy(),
                "avg_confidence": self._calculate_average(self.metrics["decision_quality"]["decision_confidence"]),
                "avg_latency": self._calculate_average(self.metrics["decision_quality"]["decision_latency"])
            },
            "system_performance": {
                "cache_hit_rate": self._calculate_average(self.metrics["system_performance"]["cache_hit_rate"]),
                "avg_response_time": self._calculate_average(self.metrics["system_performance"]["api_response_time"]),
                "error_rate": self._calculate_average(self.metrics["system_performance"]["error_rate"])
            },
            "business_value": self.calculate_business_value_metrics(),
            "active_alerts": len(self.active_alerts),
            "alerts": self.active_alerts[-10:]  # 最近10个告警
        }
        
        return summary
    
    def _calculate_success_rate(self, metric_type: str) -> float:
        """计算成功率"""
        if metric_type == "data_collection":
            metrics = self.metrics["data_collection"]
            total = metrics["total_requests"]
            if total == 0:
                return 0.0
            return metrics["successful_requests"] / total
        return 0.0
    
    def _calculate_accuracy(self) -> float:
        """计算决策准确率"""
        metrics = self.metrics["decision_quality"]
        total = metrics["total_decisions"]
        if total == 0:
            return 0.0
        return metrics["correct_decisions"] / total
    
    def get_historical_data(self, metric_name: str, period: str = "hourly") -> List[Dict[str, Any]]:
        """获取历史数据"""
        if period in self.history and metric_name in self.history[period]:
            return list(self.history[period][metric_name])
        return []
    
    def clear_old_alerts(self, hours: int = 24):
        """清理旧告警"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        self.active_alerts = [
            alert for alert in self.active_alerts
            if datetime.fromisoformat(alert["timestamp"]) > cutoff_time
        ]
    
    def reset_metrics(self):
        """重置指标（保留历史数据）"""
        self.metrics = {
            "data_collection": {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_data_points": 0,
                "last_collection_time": None,
                "collection_latency": deque(maxlen=100),
                "data_sources": defaultdict(lambda: {
                    "requests": 0,
                    "success": 0,
                    "failures": 0,
                    "last_success": None,
                    "last_failure": None
                })
            },
            "user_activity": {
                "total_logins": 0,
                "active_users": 0,
                "api_calls": defaultdict(int),
                "last_activity": defaultdict(lambda: None)
            },
            "decision_quality": {
                "total_decisions": 0,
                "correct_decisions": 0,
                "incorrect_decisions": 0,
                "decision_confidence": deque(maxlen=100),
                "decision_latency": deque(maxlen=100)
            },
            "system_performance": {
                "cache_hit_rate": deque(maxlen=100),
                "database_query_time": deque(maxlen=100),
                "api_response_time": deque(maxlen=100),
                "error_rate": deque(maxlen=100)
            },
            "business_value": {
                "data_quality_score": 0.0,
                "user_satisfaction_score": 0.0,
                "system_reliability_score": 0.0,
                "business_impact_score": 0.0
            }
        }


# 全局业务指标收集器实例
_business_metrics_collector = None


def get_business_metrics_collector() -> BusinessMetricsCollector:
    """获取业务指标收集器实例"""
    global _business_metrics_collector
    if _business_metrics_collector is None:
        _business_metrics_collector = BusinessMetricsCollector()
    return _business_metrics_collector


def record_data_collection_metric(
    source_id: str, 
    success: bool, 
    data_points: int = 0,
    latency: float = 0.0
):
    """记录数据采集指标（便捷函数）"""
    collector = get_business_metrics_collector()
    collector.record_data_collection(source_id, success, data_points, latency)


def record_user_activity_metric(user_id: str, action: str):
    """记录用户活动指标（便捷函数）"""
    collector = get_business_metrics_collector()
    collector.record_user_activity(user_id, action)


def record_decision_metric(
    decision_id: str, 
    correct: Optional[bool] = None,
    confidence: float = 0.0,
    latency: float = 0.0
):
    """记录决策质量指标（便捷函数）"""
    collector = get_business_metrics_collector()
    collector.record_decision(decision_id, correct, confidence, latency)


def record_system_performance_metric(metric_type: str, value: float):
    """记录系统性能指标（便捷函数）"""
    collector = get_business_metrics_collector()
    collector.record_system_performance(metric_type, value)


def get_business_metrics_summary() -> Dict[str, Any]:
    """获取业务指标摘要（便捷函数）"""
    collector = get_business_metrics_collector()
    return collector.get_metrics_summary()


# 业务指标API端点（供FastAPI使用）
class BusinessMetricsAPI:
    """业务指标API"""
    
    @staticmethod
    async def get_metrics_summary():
        """获取业务指标摘要"""
        collector = get_business_metrics_collector()
        return collector.get_metrics_summary()
    
    @staticmethod
    async def get_historical_data(metric_name: str, period: str = "hourly"):
        """获取历史数据"""
        collector = get_business_metrics_collector()
        return collector.get_historical_data(metric_name, period)
    
    @staticmethod
    async def get_active_alerts():
        """获取活跃告警"""
        collector = get_business_metrics_collector()
        return {
            "total_alerts": len(collector.active_alerts),
            "alerts": collector.active_alerts[-20:]  # 最近20个告警
        }
    
    @staticmethod
    async def reset_metrics():
        """重置指标"""
        collector = get_business_metrics_collector()
        collector.reset_metrics()
        return {"message": "指标已重置"}
    
    @staticmethod
    async def get_metrics_config():
        """获取指标配置"""
        collector = get_business_metrics_collector()
        return {
            "alerts_config": collector.alerts_config,
            "timestamp": datetime.now().isoformat()
        }


# 业务关键指标定义
BUSINESS_CRITICAL_METRICS = {
    "data_collection_success_rate": {
        "description": "数据采集成功率",
        "threshold": 0.95,
        "importance": "critical",
        "unit": "percentage"
    },
    "decision_accuracy": {
        "description": "决策准确率",
        "threshold": 0.7,
        "importance": "high",
        "unit": "percentage"
    },
    "system_response_time": {
        "description": "系统平均响应时间",
        "threshold": 2.0,
        "importance": "high",
        "unit": "seconds"
    },
    "user_active_sessions": {
        "description": "活跃用户会话数",
        "threshold": 10,
        "importance": "medium",
        "unit": "count"
    },
    "cache_hit_rate": {
        "description": "缓存命中率",
        "threshold": 0.8,
        "importance": "medium",
        "unit": "percentage"
    },
    "data_quality_score": {
        "description": "数据质量评分",
        "threshold": 80,
        "importance": "high",
        "unit": "score"
    },
    "business_impact_score": {
        "description": "业务影响评分",
        "threshold": 70,
        "importance": "critical",
        "unit": "score"
    }
}


# 示例使用
if __name__ == "__main__":
    # 初始化收集器
    collector = BusinessMetricsCollector()
    
    # 模拟记录一些指标
    collector.record_data_collection("source_1", True, 100, 1.5)
    collector.record_data_collection("source_2", False, 0, 5.0)
    collector.record_user_activity("user_123", "login")
    collector.record_user_activity("user_123", "view_dashboard")
    collector.record_decision("decision_1", True, 0.85, 0.2)
    collector.record_system_performance("api_response_time", 1.2)
    collector.record_system_performance("cache_hit_rate", 0.75)
    
    # 获取指标摘要
    summary = collector.get_metrics_summary()
    print("业务指标摘要:")
    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
    
    # 计算业务价值指标
    business_value = collector.calculate_business_value_metrics()
    print("\n业务价值指标:")
    print(json.dumps(business_value, indent=2, ensure_ascii=False))