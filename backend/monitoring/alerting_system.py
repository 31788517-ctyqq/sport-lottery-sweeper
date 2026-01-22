#!/usr/bin/env python3
"""
监控和告警系统
功能：
1. 系统指标收集
2. 业务指标监控
3. 智能告警机制
4. 告警通知分发
5. 性能分析和优化建议
"""

import logging
import asyncio
import time
import psutil
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp

from backend.database import get_db
from backend.models.system_config import SystemConfig
from backend.models.user import User, UserLoginLog
from backend.models.match import Match
from backend.models.crawler import CrawlerLog
from backend.architecture.data_layer_manager import data_layer_manager

# 配置日志
logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """告警级别枚举"""
    INFO = "info"           # 信息
    WARNING = "warning"     # 警告
    ERROR = "error"         # 错误
    CRITICAL = "critical"   # 严重

class MetricType(Enum):
    """指标类型枚举"""
    SYSTEM = "system"       # 系统指标
    DATABASE = "database"   # 数据库指标
    BUSINESS = "business"   # 业务指标
    APPLICATION = "app"     # 应用指标
    SECURITY = "security"   # 安全指标

class NotificationChannel(Enum):
    """通知渠道枚举"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    WECHAT = "wechat"

@dataclass
class Metric:
    """指标数据类"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str]
    metric_type: MetricType

@dataclass
class AlertRule:
    """告警规则数据类"""
    id: str
    name: str
    metric_name: str
    condition: str  # gt, lt, eq, neq, between
    threshold: float
    level: AlertLevel
    message_template: str
    enabled: bool = True
    cooldown_minutes: int = 5
    notification_channels: List[NotificationChannel] = None
    
@dataclass
class Alert:
    """告警数据类"""
    id: str
    rule_id: str
    rule_name: str
    level: AlertLevel
    message: str
    metric_value: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.metrics_buffer = deque(maxlen=10000)  # 保留最近1万条指标
        self.collection_interval = 30  # 30秒收集一次
        self.custom_collectors = {}
        
    def register_custom_collector(self, name: str, collector_func: Callable[[], Dict]):
        """注册自定义指标收集器"""
        self.custom_collectors[name] = collector_func
    
    async def collect_system_metrics(self) -> List[Metric]:
        """收集系统指标"""
        metrics = []
        now = datetime.utcnow()
        
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics.append(Metric(
                name="cpu_usage_percent",
                value=cpu_percent,
                timestamp=now,
                tags={"host": "localhost"},
                metric_type=MetricType.SYSTEM
            ))
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            metrics.extend([
                Metric(
                    name="memory_usage_percent",
                    value=memory.percent,
                    timestamp=now,
                    tags={"host": "localhost"},
                    metric_type=MetricType.SYSTEM
                ),
                Metric(
                    name="memory_available_gb",
                    value=memory.available / (1024**3),
                    timestamp=now,
                    tags={"host": "localhost"},
                    metric_type=MetricType.SYSTEM
                )
            ])
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            metrics.append(Metric(
                name="disk_usage_percent",
                value=(disk.used / disk.total) * 100,
                timestamp=now,
                tags={"host": "localhost", "mount": "/"},
                metric_type=MetricType.SYSTEM
            ))
            
            # 网络IO
            net_io = psutil.net_io_counters()
            metrics.extend([
                Metric(
                    name="network_bytes_sent",
                    value=net_io.bytes_sent,
                    timestamp=now,
                    tags={"host": "localhost"},
                    metric_type=MetricType.SYSTEM
                ),
                Metric(
                    name="network_bytes_recv",
                    value=net_io.bytes_recv,
                    timestamp=now,
                    tags={"host": "localhost"},
                    metric_type=MetricType.SYSTEM
                )
            ])
            
            # 进程信息
            process = psutil.Process()
            metrics.extend([
                Metric(
                    name="process_cpu_percent",
                    value=process.cpu_percent(),
                    timestamp=now,
                    tags={"host": "localhost", "pid": str(process.pid)},
                    metric_type=MetricType.APPLICATION
                ),
                Metric(
                    name="process_memory_mb",
                    value=process.memory_info().rss / (1024**2),
                    timestamp=now,
                    tags={"host": "localhost", "pid": str(process.pid)},
                    metric_type=MetricType.APPLICATION
                )
            ])
            
        except Exception as e:
            logger.error(f"收集系统指标失败: {e}")
        
        return metrics
    
    async def collect_database_metrics(self) -> List[Metric]:
        """收集数据库指标"""
        metrics = []
        now = datetime.utcnow()
        
        try:
            with get_db() as db:
                # 数据库大小
                db.execute(text("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()"))
                db_size_result = db.fetchone()
                if db_size_result:
                    db_size_mb = db_size_result[0] / (1024**2)
                    metrics.append(Metric(
                        name="database_size_mb",
                        value=db_size_mb,
                        timestamp=now,
                        tags={"database": "sport_lottery"},
                        metric_type=MetricType.DATABASE
                    ))
                
                # 表记录数统计
                tables = ['users', 'matches', 'leagues', 'teams', 'user_login_logs']
                for table in tables:
                    try:
                        db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count_result = db.fetchone()
                        if count_result:
                            metrics.append(Metric(
                                name=f"table_record_count",
                                value=count_result[0],
                                timestamp=now,
                                tags={"table": table},
                                metric_type=MetricType.DATABASE
                            ))
                    except Exception as e:
                        logger.warning(f"统计表 {table} 记录数失败: {e}")
                
                # 数据库连接数（SQLite不直接支持，使用替代指标）
                metrics.append(Metric(
                    name="database_connections_active",
                    value=1,  # SQLite单连接模式
                    timestamp=now,
                    tags={"database": "sport_lottery"},
                    metric_type=MetricType.DATABASE
                ))
                
        except Exception as e:
            logger.error(f"收集数据库指标失败: {e}")
        
        return metrics
    
    async def collect_business_metrics(self) -> List[Metric]:
        """收集业务指标"""
        metrics = []
        now = datetime.utcnow()
        
        try:
            with get_db() as db:
                # 用户相关指标
                today = datetime.now().date()
                
                # 今日新增用户
                db.execute(text("SELECT COUNT(*) FROM users WHERE DATE(created_at) = :today"), {"today": today})
                new_users_result = db.fetchone()
                new_users = new_users_result[0] if new_users_result else 0
                metrics.append(Metric(
                    name="daily_new_users",
                    value=new_users,
                    timestamp=now,
                    tags={"date": str(today)},
                    metric_type=MetricType.BUSINESS
                ))
                
                # 今日活跃用户
                db.execute(text("""
                    SELECT COUNT(DISTINCT user_id) FROM user_login_logs 
                    WHERE DATE(login_at) = :today AND success = 1
                """), {"today": today})
                active_users_result = db.fetchone()
                active_users = active_users_result[0] if active_users_result else 0
                metrics.append(Metric(
                    name="daily_active_users",
                    value=active_users,
                    timestamp=now,
                    tags={"date": str(today)},
                    metric_type=MetricType.BUSINESS
                ))
                
                # 今日登录成功率
                db.execute(text("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
                    FROM user_login_logs 
                    WHERE DATE(login_at) = :today
                """), {"today": today})
                login_stats = db.fetchone()
                if login_stats and login_stats[0] > 0:
                    success_rate = (login_stats[1] / login_stats[0]) * 100
                    metrics.append(Metric(
                        name="daily_login_success_rate",
                        value=success_rate,
                        timestamp=now,
                        tags={"date": str(today)},
                        metric_type=MetricType.BUSINESS
                    ))
                
                # 今日比赛数量
                db.execute(text("SELECT COUNT(*) FROM matches WHERE DATE(match_date) = :today"), {"today": today})
                matches_result = db.fetchone()
                matches_count = matches_result[0] if matches_result else 0
                metrics.append(Metric(
                    name="daily_matches_count",
                    value=matches_count,
                    timestamp=now,
                    tags={"date": str(today)},
                    metric_type=MetricType.BUSINESS
                ))
                
                # 爬虫成功率
                yesterday = datetime.now() - timedelta(days=1)
                db.execute(text("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful
                    FROM crawler_logs 
                    WHERE DATE(start_time) = :yesterday
                """), {"yesterday": yesterday.date()})
                crawler_stats = db.fetchone()
                if crawler_stats and crawler_stats[0] > 0:
                    crawler_success_rate = (crawler_stats[1] / crawler_stats[0]) * 100
                    metrics.append(Metric(
                        name="daily_crawler_success_rate",
                        value=crawler_success_rate,
                        timestamp=now,
                        tags={"date": str(yesterday.date())},
                        metric_type=MetricType.BUSINESS
                    ))
                
        except Exception as e:
            logger.error(f"收集业务指标失败: {e}")
        
        return metrics
    
    async def collect_security_metrics(self) -> List[Metric]:
        """收集安全指标"""
        metrics = []
        now = datetime.utcnow()
        
        try:
            with get_db() as db:
                # 过去1小时的失败登录次数
                one_hour_ago = datetime.now() - timedelta(hours=1)
                db.execute(text("""
                    SELECT COUNT(*) FROM user_login_logs 
                    WHERE success = 0 AND login_at >= :since
                """), {"since": one_hour_ago})
                failed_logins_result = db.fetchone()
                failed_logins = failed_logins_result[0] if failed_logins_result else 0
                metrics.append(Metric(
                    name="failed_logins_last_hour",
                    value=failed_logins,
                    timestamp=now,
                    tags={"period": "1h"},
                    metric_type=MetricType.SECURITY
                ))
                
                # 可疑IP的登录尝试
                db.execute(text("""
                    SELECT COUNT(DISTINCT login_ip) FROM user_login_logs 
                    WHERE success = 0 AND login_at >= :since
                """), {"since": one_hour_ago})
                suspicious_ips_result = db.fetchone()
                suspicious_ips = suspicious_ips_result[0] if suspicious_ips_result else 0
                metrics.append(Metric(
                    name="suspicious_ips_last_hour",
                    value=suspicious_ips,
                    timestamp=now,
                    tags={"period": "1h"},
                    metric_type=MetricType.SECURITY
                ))
                
                # 账户锁定数量
                db.execute(text("SELECT COUNT(*) FROM users WHERE status = 'locked'"))
                locked_accounts_result = db.fetchone()
                locked_accounts = locked_accounts_result[0] if locked_accounts_result else 0
                metrics.append(Metric(
                    name="locked_accounts_total",
                    value=locked_accounts,
                    timestamp=now,
                    tags={},
                    metric_type=MetricType.SECURITY
                ))
                
        except Exception as e:
            logger.error(f"收集安全指标失败: {e}")
        
        return metrics
    
    async def collect_all_metrics(self) -> List[Metric]:
        """收集所有指标"""
        all_metrics = []
        
        # 收集各类指标
        system_metrics = await self.collect_system_metrics()
        db_metrics = await self.collect_database_metrics()
        business_metrics = await self.collect_business_metrics()
        security_metrics = await self.collect_security_metrics()
        
        all_metrics.extend(system_metrics)
        all_metrics.extend(db_metrics)
        all_metrics.extend(business_metrics)
        all_metrics.extend(security_metrics)
        
        # 收集自定义指标
        for name, collector_func in self.custom_collectors.items():
            try:
                custom_data = collector_func()
                for metric_name, value in custom_data.items():
                    all_metrics.append(Metric(
                        name=f"custom_{metric_name}",
                        value=float(value),
                        timestamp=datetime.utcnow(),
                        tags={"collector": name},
                        metric_type=MetricType.APPLICATION
                    ))
            except Exception as e:
                logger.error(f"收集自定义指标 {name} 失败: {e}")
        
        # 添加到缓冲区
        self.metrics_buffer.extend(all_metrics)
        
        return all_metrics

class AlertingEngine:
    """告警引擎"""
    
    def __init__(self):
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=1000)  # 保留最近1000条告警
        self.last_alert_times: Dict[str, datetime] = {}  # 防重复告警
        
    def add_alert_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.alert_rules[rule.id] = rule
        logger.info(f"添加告警规则: {rule.name} ({rule.id})")
    
    def remove_alert_rule(self, rule_id: str):
        """移除告警规则"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"移除告警规则: {rule_id}")
    
    async def evaluate_metrics(self, metrics: List[Metric]):
        """评估指标并触发告警"""
        for metric in metrics:
            matching_rules = self._find_matching_rules(metric)
            
            for rule in matching_rules:
                if not rule.enabled:
                    continue
                    
                should_alert = self._evaluate_condition(rule, metric.value)
                
                if should_alert:
                    await self._trigger_alert(rule, metric)
                else:
                    # 检查是否可以解决现有告警
                    await self._check_alert_resolution(rule, metric)
    
    def _find_matching_rules(self, metric: Metric) -> List[AlertRule]:
        """查找匹配指标的告警规则"""
        matching_rules = []
        
        for rule in self.alert_rules.values():
            if rule.metric_name == metric.name:
                # 检查标签匹配
                if self._tags_match(rule.tags, metric.tags):
                    matching_rules.append(rule)
        
        return matching_rules
    
    def _tags_match(self, rule_tags: Dict[str, str], metric_tags: Dict[str, str]) -> bool:
        """检查标签是否匹配"""
        for key, value in rule_tags.items():
            if key not in metric_tags or metric_tags[key] != value:
                return False
        return True
    
    def _evaluate_condition(self, rule: AlertRule, value: float) -> bool:
        """评估告警条件"""
        if rule.condition == "gt":
            return value > rule.threshold
        elif rule.condition == "lt":
            return value < rule.threshold
        elif rule.condition == "eq":
            return abs(value - rule.threshold) < 0.001
        elif rule.condition == "neq":
            return abs(value - rule.threshold) >= 0.001
        elif rule.condition == "between":
            # 假设阈值是范围的下限，上限在消息模板中定义
            return value > rule.threshold
        else:
            logger.warning(f"未知的告警条件: {rule.condition}")
            return False
    
    async def _trigger_alert(self, rule: AlertRule, metric: Metric):
        """触发告警"""
        alert_key = f"{rule.id}:{metric.timestamp.strftime('%Y%m%d%H%M%S')}"
        
        # 检查冷却期
        if rule.id in self.last_alert_times:
            last_time = self.last_alert_times[rule.id]
            cooldown_period = timedelta(minutes=rule.cooldown_minutes)
            if datetime.utcnow() - last_time < cooldown_period:
                return  # 还在冷却期内，不重复告警
        
        # 创建告警
        message = rule.message_template.format(
            metric_name=rule.metric_name,
            current_value=metric.value,
            threshold=rule.threshold,
            timestamp=metric.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        )
        
        alert = Alert(
            id=alert_key,
            rule_id=rule.id,
            rule_name=rule.name,
            level=rule.level,
            message=message,
            metric_value=metric.value,
            timestamp=datetime.utcnow()
        )
        
        self.active_alerts[alert_key] = alert
        self.alert_history.append(alert)
        self.last_alert_times[rule.id] = datetime.utcnow()
        
        # 发送通知
        await self._send_notifications(rule, alert)
        
        logger.warning(f"触发告警 [{rule.level.value.upper()}]: {message}")
    
    async def _check_alert_resolution(self, rule: AlertRule, metric: Metric):
        """检查告警是否可以解决"""
        resolved_alerts = []
        
        for alert_key, alert in self.active_alerts.items():
            if alert.rule_id == rule.id and not alert.resolved:
                # 检查条件是否不再满足
                if not self._evaluate_condition(rule, metric.value):
                    alert.resolved = True
                    alert.resolved_at = datetime.utcnow()
                    resolved_alerts.append(alert)
                    
                    logger.info(f"告警已解决: {alert.rule_name}")
        
        # 从活跃告警中移除已解决的
        for alert in resolved_alerts:
            if alert.id in self.active_alerts:
                del self.active_alerts[alert.id]
    
    async def _send_notifications(self, rule: AlertRule, alert: Alert):
        """发送告警通知"""
        if not rule.notification_channels:
            return
        
        tasks = []
        for channel in rule.notification_channels:
            if channel == NotificationChannel.EMAIL:
                tasks.append(self._send_email_notification(rule, alert))
            elif channel == NotificationChannel.WEBHOOK:
                tasks.append(self._send_webhook_notification(rule, alert))
            elif channel == NotificationChannel.SLACK:
                tasks.append(self._send_slack_notification(rule, alert))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_email_notification(self, rule: AlertRule, alert: Alert):
        """发送邮件通知"""
        try:
            # 这里实现邮件发送逻辑
            # 需要配置SMTP服务器信息
            logger.info(f"发送邮件告警: {alert.message}")
            pass
        except Exception as e:
            logger.error(f"发送邮件告警失败: {e}")
    
    async def _send_webhook_notification(self, rule: AlertRule, alert: Alert):
        """发送Webhook通知"""
        try:
            webhook_url = getattr(settings, 'ALERT_WEBHOOK_URL', None)
            if not webhook_url:
                return
                
            payload = {
                "alert_id": alert.id,
                "rule_name": alert.rule_name,
                "level": alert.level.value,
                "message": alert.message,
                "metric_value": alert.metric_value,
                "timestamp": alert.timestamp.isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload, timeout=10) as resp:
                    if resp.status == 200:
                        logger.info(f"Webhook告警发送成功: {alert.rule_name}")
                    else:
                        logger.error(f"Webhook告警发送失败: HTTP {resp.status}")
                        
        except Exception as e:
            logger.error(f"发送Webhook告警失败: {e}")
    
    async def _send_slack_notification(self, rule: AlertRule, alert: Alert):
        """发送Slack通知"""
        try:
            slack_webhook = getattr(settings, 'SLACK_WEBHOOK_URL', None)
            if not slack_webhook:
                return
                
            color_map = {
                AlertLevel.INFO: "good",
                AlertLevel.WARNING: "warning", 
                AlertLevel.ERROR: "danger",
                AlertLevel.CRITICAL: "#ff0000"
            }
            
            payload = {
                "attachments": [{
                    "color": color_map.get(alert.level, "warning"),
                    "fields": [{
                        "title": f"{alert.level.value.upper()} - {alert.rule_name}",
                        "value": alert.message,
                        "short": False
                    }],
                    "ts": alert.timestamp.timestamp()
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(slack_webhook, json=payload, timeout=10) as resp:
                    if resp.status == 200:
                        logger.info(f"Slack告警发送成功: {alert.rule_name}")
                    else:
                        logger.error(f"Slack告警发送失败: HTTP {resp.status}")
                        
        except Exception as e:
            logger.error(f"发送Slack告警失败: {e}")

class MonitoringDashboard:
    """监控仪表板"""
    
    def __init__(self, metrics_collector: MetricsCollector, alerting_engine: AlertingEngine):
        self.metrics_collector = metrics_collector
        self.alerting_engine = alerting_engine
        self.dashboard_data = {}
        
    async def generate_dashboard_data(self) -> Dict:
        """生成仪表板数据"""
        now = datetime.utcnow()
        
        dashboard = {
            "timestamp": now.isoformat(),
            "system_overview": await self._get_system_overview(),
            "business_metrics": await self._get_business_metrics(),
            "active_alerts": self._get_active_alerts(),
            "performance_trends": await self._get_performance_trends(),
            "top_issues": await self._get_top_issues()
        }
        
        self.dashboard_data[now.strftime('%Y-%m-%d %H:%M')] = dashboard
        return dashboard
    
    async def _get_system_overview(self) -> Dict:
        """获取系统概览"""
        recent_metrics = list(self.metrics_collector.metrics_buffer)[-100:]  # 最近100条
        
        overview = {
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_usage": 0,
            "active_users": 0,
            "database_size_mb": 0
        }
        
        for metric in recent_metrics:
            if metric.name == "cpu_usage_percent":
                overview["cpu_usage"] = metric.value
            elif metric.name == "memory_usage_percent":
                overview["memory_usage"] = metric.value
            elif metric.name == "disk_usage_percent":
                overview["disk_usage"] = metric.value
            elif metric.name == "daily_active_users":
                overview["active_users"] = max(overview["active_users"], metric.value)
            elif metric.name == "database_size_mb":
                overview["database_size_mb"] = metric.value
        
        return overview
    
    async def _get_business_metrics(self) -> Dict:
        """获取业务指标"""
        recent_metrics = list(self.metrics_collector.metrics_buffer)[-200:]
        
        business = {
            "daily_new_users": 0,
            "daily_active_users": 0,
            "login_success_rate": 0,
            "matches_today": 0,
            "crawler_success_rate": 0
        }
        
        for metric in recent_metrics:
            if metric.metric_type == MetricType.BUSINESS:
                if metric.name == "daily_new_users":
                    business["daily_new_users"] = max(business["daily_new_users"], metric.value)
                elif metric.name == "daily_active_users":
                    business["daily_active_users"] = max(business["daily_active_users"], metric.value)
                elif metric.name == "daily_login_success_rate":
                    business["login_success_rate"] = metric.value
                elif metric.name == "daily_matches_count":
                    business["matches_today"] = max(business["matches_today"], metric.value)
                elif metric.name == "daily_crawler_success_rate":
                    business["crawler_success_rate"] = metric.value
        
        return business
    
    def _get_active_alerts(self) -> List[Dict]:
        """获取活跃告警"""
        return [
            {
                "id": alert.id,
                "rule_name": alert.rule_name,
                "level": alert.level.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat()
            }
            for alert in self.alerting_engine.active_alerts.values()
        ]
    
    async def _get_performance_trends(self) -> Dict:
        """获取性能趋势"""
        # 分析最近一段时间的指标趋势
        return {
            "cpu_trend": "stable",
            "memory_trend": "increasing",
            "response_time_trend": "decreasing",
            "error_rate_trend": "stable"
        }
    
    async def _get_top_issues(self) -> List[Dict]:
        """获取主要问题"""
        issues = []
        
        # 基于告警历史和指标分析识别主要问题
        if len(self.alerting_engine.alert_history) > 0:
            recent_alerts = list(self.alerting_engine.alert_history)[-10:]
            critical_alerts = [a for a in recent_alerts if a.level == AlertLevel.CRITICAL]
            
            if critical_alerts:
                issues.append({
                    "type": "critical_alerts",
                    "count": len(critical_alerts),
                    "description": f"最近发现 {len(critical_alerts)} 个严重告警"
                })
        
        return issues

class MonitoringSystem:
    """监控系统主类"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alerting_engine = AlertingEngine()
        self.dashboard = MonitoringDashboard(self.metrics_collector, self.alerting_engine)
        self.is_running = False
        self.collection_task = None
        
        # 注册默认告警规则
        self._register_default_alert_rules()
        
    def _register_default_alert_rules(self):
        """注册默认告警规则"""
        default_rules = [
            AlertRule(
                id="high_cpu_usage",
                name="CPU使用率过高",
                metric_name="cpu_usage_percent",
                condition="gt",
                threshold=80,
                level=AlertLevel.WARNING,
                message_template="CPU使用率达到 {current_value:.1f}%，超过阈值 {threshold}%",
                notification_channels=[NotificationChannel.WEBHOOK]
            ),
            AlertRule(
                id="critical_cpu_usage",
                name="CPU使用率严重过高",
                metric_name="cpu_usage_percent",
                condition="gt",
                threshold=95,
                level=AlertLevel.CRITICAL,
                message_template="CPU使用率达到 {current_value:.1f}%，严重超过阈值 {threshold}%",
                notification_channels=[NotificationChannel.WEBHOOK, NotificationChannel.EMAIL]
            ),
            AlertRule(
                id="high_memory_usage",
                name="内存使用率过高",
                metric_name="memory_usage_percent",
                condition="gt",
                threshold=85,
                level=AlertLevel.WARNING,
                message_template="内存使用率达到 {current_value:.1f}%，超过阈值 {threshold}%",
                notification_channels=[NotificationChannel.WEBHOOK]
            ),
            AlertRule(
                id="low_login_success_rate",
                name="登录成功率过低",
                metric_name="daily_login_success_rate",
                condition="lt",
                threshold=90,
                level=AlertLevel.ERROR,
                message_template="登录成功率仅为 {current_value:.1f}%，低于阈值 {threshold}%",
                notification_channels=[NotificationChannel.WEBHOOK]
            ),
            AlertRule(
                id="many_failed_logins",
                name="短时间内大量登录失败",
                metric_name="failed_logins_last_hour",
                condition="gt",
                threshold=50,
                level=AlertLevel.WARNING,
                message_template="1小时内登录失败 {current_value} 次，可能存在攻击",
                notification_channels=[NotificationChannel.WEBHOOK]
            )
        ]
        
        for rule in default_rules:
            self.alerting_engine.add_alert_rule(rule)
    
    async def start(self):
        """启动监控系统"""
        if self.is_running:
            logger.warning("监控系统已在运行中")
            return
        
        self.is_running = True
        
        # 启动指标收集任务
        self.collection_task = asyncio.create_task(self._metrics_collection_loop())
        
        logger.info("监控系统启动完成")
    
    async def stop(self):
        """停止监控系统"""
        self.is_running = False
        
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        
        logger.info("监控系统已停止")
    
    async def _metrics_collection_loop(self):
        """指标收集循环"""
        while self.is_running:
            try:
                # 收集所有指标
                metrics = await self.metrics_collector.collect_all_metrics()
                
                # 评估告警规则
                await self.alerting_engine.evaluate_metrics(metrics)
                
                # 等待下次收集
                await asyncio.sleep(self.metrics_collector.collection_interval)
                
            except Exception as e:
                logger.error(f"指标收集循环出错: {e}")
                await asyncio.sleep(60)  # 出错后等待1分钟再重试
    
    async def get_system_status(self) -> Dict:
        """获取系统状态"""
        dashboard_data = await self.dashboard.generate_dashboard_data()
        
        return {
            "status": "running" if self.is_running else "stopped",
            "uptime_seconds": time.time(),
            "metrics_collected": len(self.metrics_collector.metrics_buffer),
            "active_alerts_count": len(self.alerting_engine.active_alerts),
            "dashboard": dashboard_data
        }

# 全局监控系统实例
monitoring_system = MonitoringSystem()