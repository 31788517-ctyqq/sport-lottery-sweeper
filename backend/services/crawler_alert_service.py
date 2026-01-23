"""
爬虫告警服务
处理爬虫监控告警的规则管理、触发检查和通知发送
"""
import logging
import smtplib
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.crawler_config import CrawlerConfig
from ..models.crawler_logs import CrawlerTaskLog
from ..models.crawler_tasks import CrawlerTask
from ..models.crawler_alert_rules import CrawlerAlertRule
from ..models.crawler_alert_records import CrawlerAlertRecord
from ..models.crawler_metrics import CrawlerMetric
from ..schemas.crawler_alert import AlertRuleCreate, AlertRuleUpdate
from ..services.notification_service import NotificationService
from ..core.cache_manager import CacheManager

logger = logging.getLogger(__name__)


class CrawlerAlertService:
    """爬虫告警服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService()
        self.cache = CacheManager()
    
    def create_alert_rule(self, rule_data: AlertRuleCreate, created_by: int) -> Dict[str, Any]:
        """创建告警规则"""
        try:
            # 验证阈值和比较操作符
            self._validate_alert_rule(rule_data)
            
            db_rule = CrawlerAlertRule(
                name=rule_data.name,
                description=rule_data.description,
                metric_type=rule_data.metric_type,
                threshold=rule_data.threshold,
                comparison_operator=rule_data.comparison_operator,
                time_window_minutes=rule_data.time_window_minutes,
                source_ids=rule_data.source_ids,
                alert_level=rule_data.alert_level,
                cooldown_minutes=rule_data.cooldown_minutes,
                notification_channels=rule_data.notification_channels,
                created_by=created_by,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(db_rule)
            self.db.commit()
            self.db.refresh(db_rule)
            
            logger.info(f"创建告警规则成功: {rule_data.name}")
            
            return {
                "success": True,
                "message": "告警规则创建成功",
                "rule_id": db_rule.id
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建告警规则失败: {str(e)}")
            return {
                "success": False,
                "message": f"创建告警规则失败: {str(e)}"
            }
    
    def update_alert_rule(self, rule_id: int, rule_data: AlertRuleUpdate, updated_by: int) -> Dict[str, Any]:
        """更新告警规则"""
        try:
            db_rule = self.db.query(CrawlerAlertRule).filter(
                CrawlerAlertRule.id == rule_id
            ).first()
            
            if not db_rule:
                return {
                    "success": False,
                    "message": "告警规则不存在"
                }
            
            # 验证规则数据
            self._validate_alert_rule(rule_data)
            
            # 更新字段
            update_data = rule_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_rule, field, value)
            
            db_rule.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(db_rule)
            
            logger.info(f"更新告警规则成功: {rule_id}")
            
            return {
                "success": True,
                "message": "告警规则更新成功"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新告警规则失败: {str(e)}")
            return {
                "success": False,
                "message": f"更新告警规则失败: {str(e)}"
            }
    
    def delete_alert_rule(self, rule_id: int) -> Dict[str, Any]:
        """删除告警规则"""
        try:
            db_rule = self.db.query(CrawlerAlertRule).filter(
                CrawlerAlertRule.id == rule_id
            ).first()
            
            if not db_rule:
                return {
                    "success": False,
                    "message": "告警规则不存在"
                }
            
            self.db.delete(db_rule)
            self.db.commit()
            
            logger.info(f"删除告警规则成功: {rule_id}")
            
            return {
                "success": True,
                "message": "告警规则删除成功"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除告警规则失败: {str(e)}")
            return {
                "success": False,
                "message": f"删除告警规则失败: {str(e)}"
            }
    
    def get_alert_rules(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """获取告警规则列表"""
        query = self.db.query(CrawlerAlertRule)
        
        if active_only:
            query = query.filter(CrawlerAlertRule.is_active == True)
        
        rules = query.order_by(CrawlerAlertRule.created_at.desc()).all()
        
        return [
            {
                "id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "metric_type": rule.metric_type,
                "threshold": rule.threshold,
                "comparison_operator": rule.comparison_operator,
                "time_window_minutes": rule.time_window_minutes,
                "source_ids": rule.source_ids,
                "is_active": rule.is_active,
                "alert_level": rule.alert_level,
                "cooldown_minutes": rule.cooldown_minutes,
                "notification_channels": rule.notification_channels,
                "created_at": rule.created_at.isoformat() if rule.created_at else None,
                "updated_at": rule.updated_at.isoformat() if rule.updated_at else None
            }
            for rule in rules
        ]
    
    def check_alerts(self) -> Dict[str, Any]:
        """检查所有告警规则并触发告警"""
        try:
            active_rules = self.db.query(CrawlerAlertRule).filter(
                CrawlerAlertRule.is_active == True
            ).all()
            
            triggered_alerts = []
            
            for rule in active_rules:
                # 检查冷却期
                if self._is_in_cooldown(rule):
                    continue
                
                # 检查告警条件
                alert_result = self._check_single_rule(rule)
                if alert_result["triggered"]:
                    # 创建告警记录
                    record = self._create_alert_record(rule, alert_result)
                    if record:
                        triggered_alerts.append(record)
                        
                        # 发送通知
                        self._send_alert_notification(rule, alert_result)
            
            logger.info(f"告警检查完成，触发了 {len(triggered_alerts)} 个告警")
            
            return {
                "success": True,
                "message": f"告警检查完成，触发了 {len(triggered_alerts)} 个告警",
                "triggered_count": len(triggered_alerts),
                "alerts": triggered_alerts
            }
            
        except Exception as e:
            logger.error(f"告警检查失败: {str(e)}")
            return {
                "success": False,
                "message": f"告警检查失败: {str(e)}"
            }
    
    def resolve_alert(self, alert_id: int, acknowledged_by: int) -> Dict[str, Any]:
        """解决告警"""
        try:
            alert = self.db.query(CrawlerAlertRecord).filter(
                CrawlerAlertRecord.id == alert_id
            ).first()
            
            if not alert:
                return {
                    "success": False,
                    "message": "告警记录不存在"
                }
            
            alert.status = "resolved"
            alert.resolved_at = datetime.utcnow()
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"告警已解决: {alert_id}")
            
            return {
                "success": True,
                "message": "告警已解决"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"解决告警失败: {str(e)}")
            return {
                "success": False,
                "message": f"解决告警失败: {str(e)}"
            }
    
    def get_alert_records(self, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取告警记录"""
        query = self.db.query(CrawlerAlertRecord)
        
        if status:
            query = query.filter(CrawlerAlertRecord.status == status)
        
        records = query.order_by(CrawlerAlertRecord.triggered_at.desc()).limit(limit).all()
        
        return [
            {
                "id": record.id,
                "rule_id": record.rule_id,
                "source_id": record.source_id,
                "alert_level": record.alert_level,
                "metric_value": record.metric_value,
                "threshold": record.threshold,
                "message": record.message,
                "details": record.details,
                "status": record.status,
                "triggered_at": record.triggered_at.isoformat() if record.triggered_at else None,
                "resolved_at": record.resolved_at.isoformat() if record.resolved_at else None
            }
            for record in records
        ]
    
    def record_metric(self, source_id: int, metric_type: str, metric_value: float, 
                     tags: Optional[Dict] = None) -> None:
        """记录监控指标"""
        try:
            metric = CrawlerMetric(
                source_id=source_id,
                metric_type=metric_type,
                metric_value=metric_value,
                tags=tags,
                recorded_at=datetime.utcnow()
            )
            
            self.db.add(metric)
            self.db.commit()
            
            # 缓存最新指标用于快速检查
            cache_key = f"latest_metric:{source_id}:{metric_type}"
            self.cache.set(cache_key, metric_value, ttl=300)  # 5分钟缓存
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"记录监控指标失败: {str(e)}")
    
    def _validate_alert_rule(self, rule_data) -> None:
        """验证告警规则数据"""
        # 验证比较操作符
        valid_operators = ['gt', 'lt', 'eq', 'gte', 'lte']
        if hasattr(rule_data, 'comparison_operator') and rule_data.comparison_operator not in valid_operators:
            raise ValueError(f"无效比较操作符，必须是: {valid_operators}")
        
        # 验证告警级别
        valid_levels = ['warning', 'error', 'critical']
        if hasattr(rule_data, 'alert_level') and rule_data.alert_level not in valid_levels:
            raise ValueError(f"无效告警级别，必须是: {valid_levels}")
        
        # 验证阈值
        if hasattr(rule_data, 'threshold') and rule_data.threshold < 0:
            raise ValueError("阈值不能为负数")
    
    def _is_in_cooldown(self, rule: CrawlerAlertRule) -> bool:
        """检查是否在冷却期内"""
        if rule.cooldown_minutes <= 0:
            return False
        
        # 查找最近的活跃告警
        recent_alert = self.db.query(CrawlerAlertRecord).filter(
            and_(
                CrawlerAlertRecord.rule_id == rule.id,
                CrawlerAlertRecord.status == 'active',
                CrawlerAlertRecord.triggered_at >= datetime.utcnow() - timedelta(minutes=rule.cooldown_minutes)
            )
        ).first()
        
        return recent_alert is not None
    
    def _check_single_rule(self, rule: CrawlerAlertRule) -> Dict[str, Any]:
        """检查单个告警规则"""
        try:
            # 根据指标类型获取数据
            if rule.metric_type == 'error_rate':
                return self._check_error_rate(rule)
            elif rule.metric_type == 'response_time':
                return self._check_response_time(rule)
            elif rule.metric_type == 'consecutive_failures':
                return self._check_consecutive_failures(rule)
            elif rule.metric_type == 'data_quality':
                return self._check_data_quality(rule)
            else:
                return {"triggered": False, "message": f"不支持的指标类型: {rule.metric_type}"}
                
        except Exception as e:
            logger.error(f"检查告警规则失败 {rule.id}: {str(e)}")
            return {"triggered": False, "message": f"检查失败: {str(e)}"}
    
    def _check_error_rate(self, rule: CrawlerAlertRule) -> Dict[str, Any]:
        """检查错误率"""
        # 计算时间窗口内的错误率
        start_time = datetime.utcnow() - timedelta(minutes=rule.time_window_minutes)
        
        # 构建查询条件
        query = self.db.query(CrawlerTaskLog).filter(
            CrawlerTaskLog.started_at >= start_time
        )
        
        # 按数据源过滤
        if rule.source_ids:
            query = query.filter(CrawlerTaskLog.source_id.in_(rule.source_ids))
        
        logs = query.all()
        
        if not logs:
            return {"triggered": False, "message": "没有找到执行记录"}
        
        total_requests = len(logs)
        failed_requests = len([log for log in logs if log.status == 'failed'])
        error_rate = (failed_requests / total_requests) * 100 if total_requests > 0 else 0
        
        # 检查是否触发告警
        triggered = self._compare_values(error_rate, rule.threshold, rule.comparison_operator)
        
        return {
            "triggered": triggered,
            "metric_value": error_rate,
            "total_requests": total_requests,
            "failed_requests": failed_requests,
            "message": f"错误率 {error_rate:.2f}% {'超过' if triggered else '未超过'}阈值 {rule.threshold}%"
        }
    
    def _check_response_time(self, rule: CrawlerAlertRule) -> Dict[str, Any]:
        """检查响应时间"""
        start_time = datetime.utcnow() - timedelta(minutes=rule.time_window_minutes)
        
        query = self.db.query(CrawlerTaskLog).filter(
            and_(
                CrawlerTaskLog.started_at >= start_time,
                CrawlerTaskLog.response_time_ms.isnot(None)
            )
        )
        
        if rule.source_ids:
            query = query.filter(CrawlerTaskLog.source_id.in_(rule.source_ids))
        
        logs = query.all()
        
        if not logs:
            return {"triggered": False, "message": "没有找到响应时间数据"}
        
        avg_response_time = sum(log.response_time_ms for log in logs) / len(logs)
        
        triggered = self._compare_values(avg_response_time, rule.threshold, rule.comparison_operator)
        
        return {
            "triggered": triggered,
            "metric_value": avg_response_time,
            "sample_count": len(logs),
            "message": f"平均响应时间 {avg_response_time:.2f}ms {'超过' if triggered else '未超过'}阈值 {rule.threshold}ms"
        }
    
    def _check_consecutive_failures(self, rule: CrawlerAlertRule) -> Dict[str, Any]:
        """检查连续失败次数"""
        query = self.db.query(CrawlerTaskLog).filter(
            CrawlerTaskLog.status == 'failed'
        ).order_by(CrawlerTaskLog.started_at.desc())
        
        if rule.source_ids:
            query = query.filter(CrawlerTaskLog.source_id.in_(rule.source_ids))
        
        recent_failures = query.limit(rule.threshold + 10).all()  # 多取一些以防万一
        
        # 计算连续失败
        consecutive_count = 0
        max_consecutive = 0
        
        for log in recent_failures:
            if log.status == 'failed':
                consecutive_count += 1
                max_consecutive = max(max_consecutive, consecutive_count)
            else:
                consecutive_count = 0
        
        triggered = max_consecutive >= rule.threshold
        
        return {
            "triggered": triggered,
            "metric_value": float(max_consecutive),
            "threshold": float(rule.threshold),
            "message": f"连续失败 {max_consecutive} 次 {'达到' if triggered else '未达到'}阈值 {rule.threshold} 次"
        }
    
    def _check_data_quality(self, rule: CrawlerAlertRule) -> Dict[str, Any]:
        """检查数据质量"""
        # 这里可以实现数据质量检查逻辑
        # 例如：检查数据完整性、准确性等
        # 暂时返回模拟数据
        quality_score = 95.0  # 模拟数据质量分数
        
        triggered = self._compare_values(quality_score, rule.threshold, rule.comparison_operator)
        
        return {
            "triggered": triggered,
            "metric_value": quality_score,
            "message": f"数据质量分数 {quality_score:.2f} {'低于' if triggered else '高于'}阈值 {rule.threshold}"
        }
    
    def _compare_values(self, actual: float, threshold: float, operator: str) -> bool:
        """比较数值是否满足条件"""
        if operator == 'gt':
            return actual > threshold
        elif operator == 'lt':
            return actual < threshold
        elif operator == 'eq':
            return abs(actual - threshold) < 0.001
        elif operator == 'gte':
            return actual >= threshold
        elif operator == 'lte':
            return actual <= threshold
        else:
            return False
    
    def _create_alert_record(self, rule: CrawlerAlertRule, alert_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建告警记录"""
        try:
            # 确定数据源ID（如果有）
            source_id = None
            if rule.source_ids and len(rule.source_ids) == 1:
                source_id = rule.source_ids[0]
            
            alert_record = CrawlerAlertRecord(
                rule_id=rule.id,
                source_id=source_id,
                alert_level=rule.alert_level,
                metric_value=alert_result["metric_value"],
                threshold=rule.threshold,
                message=alert_result["message"],
                details=alert_result,
                status="active",
                triggered_at=datetime.utcnow()
            )
            
            self.db.add(alert_record)
            self.db.commit()
            self.db.refresh(alert_record)
            
            return {
                "id": alert_record.id,
                "rule_id": alert_record.rule_id,
                "alert_level": alert_record.alert_level,
                "message": alert_record.message,
                "triggered_at": alert_record.triggered_at.isoformat()
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建告警记录失败: {str(e)}")
            return None
    
    def _send_alert_notification(self, rule: CrawlerAlertRule, alert_result: Dict[str, Any]) -> None:
        """发送告警通知"""
        try:
            # 构建通知内容
            subject = f"[爬虫告警-{rule.alert_level.upper()}] {rule.name}"
            message = f"""
告警详情:
- 规则名称: {rule.name}
- 告警级别: {rule.alert_level}
- 指标类型: {rule.metric_type}
- 当前值: {alert_result['metric_value']}
- 阈值: {rule.threshold}
- 消息: {alert_result['message']}
- 触发时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

请及时检查爬虫系统状态。
            """
            
            # 根据配置的渠道发送通知
            for channel in rule.notification_channels:
                if channel == 'email':
                    self.notification_service.send_email(
                        subject=subject,
                        message=message,
                        recipients=self._get_alert_recipients()
                    )
                elif channel == 'slack':
                    self.notification_service.send_slack_message(
                        message=message,
                        webhook_url=self._get_slack_webhook()
                    )
                elif channel == 'webhook':
                    self.notification_service.send_webhook_notification(
                        payload={
                            "alert": {
                                "rule_id": rule.id,
                                "rule_name": rule.name,
                                "level": rule.alert_level,
                                "message": alert_result['message'],
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        }
                    )
            
            logger.info(f"告警通知发送成功: {rule.name}")
            
        except Exception as e:
            logger.error(f"发送告警通知失败: {str(e)}")
    
    def _get_alert_recipients(self) -> List[str]:
        """获取告警接收者邮箱列表"""
        # 从系统配置中获取告警邮箱
        # 这里可以扩展为从数据库或配置文件读取
        return ["admin@sport-lottery.com"]  # 示例邮箱
    
    def _get_slack_webhook(self) -> Optional[str]:
        """获取Slack Webhook URL"""
        # 从系统配置中获取Slack配置
        return None  # 示例中返回None