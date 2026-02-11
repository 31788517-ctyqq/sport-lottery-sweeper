"""
增强的爬虫服务 - 集成监控告警功能
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from ..models.crawler_logs import CrawlerTaskLog
from ..models.crawler_tasks import CrawlerTask
from ..services.crawler_alert_service import CrawlerAlertService
from ..tasks.alert_monitoring_tasks import collect_crawler_metrics
from ..core.cache_manager import HybridCache as CacheManager

logger = logging.getLogger(__name__)


class EnhancedCrawlerService:
    """增强的爬虫服务类 - 包含监控告警功能"""
    
    def __init__(self, db: Session):
        self.db = db
        self.alert_service = CrawlerAlertService(db)
        self.cache = CacheManager()
    
    def execute_crawler_task(self, task_id: int, source_id: int, task_func, *args, **kwargs):
        """执行爬虫任务并记录监控指标"""
        start_time = datetime.utcnow()
        status = "running"
        error_message = None
        error_details = None
        response_time_ms = None
        records_processed = 0
        records_success = 0
        records_failed = 0
        
        try:
            # 执行实际的爬虫任务
            result = task_func(*args, **kwargs)
            
            # 解析任务结果
            if isinstance(result, dict):
                status = "success" if result.get("success", True) else "failed"
                records_processed = result.get("crawled", result.get("processed", result.get("updated", 0)))
                records_success = result.get("success_count", records_processed)
                records_failed = result.get("error_count", result.get("errors", 0))
                error_message = result.get("message") if status == "failed" else None
                if not result.get("success", True):
                    error_details = {"error_messages": result.get("error_messages", [])}
            else:
                status = "success"
                records_processed = 1
                records_success = 1
            
            # 估算响应时间（实际应用中可以从HTTP请求获取）
            response_time_ms = self._estimate_response_time(start_time)
            
        except Exception as e:
            status = "failed"
            error_message = str(e)
            error_details = {"exception_type": type(e).__name__, "traceback": str(e)}
            logger.error(f"爬虫任务执行失败: {str(e)}")
        
        finally:
            end_time = datetime.utcnow()
            duration_seconds = (end_time - start_time).total_seconds()
            
            # 记录任务日志到数据库
            self._log_crawler_task(
                task_id=task_id,
                source_id=source_id,
                status=status,
                started_at=start_time,
                completed_at=end_time,
                duration_seconds=duration_seconds,
                records_processed=records_processed,
                records_success=records_success,
                records_failed=records_failed,
                error_message=error_message,
                error_details=error_details,
                response_time_ms=response_time_ms
            )
            
            # 记录实时监控指标
            self._record_realtime_metrics(
                source_id=source_id,
                status=status,
                response_time_ms=response_time_ms,
                records_processed=records_processed,
                records_failed=records_failed
            )
            
            # 更新数据源统计
            self._update_source_stats(source_id, status, response_time_ms, records_processed)
        
        return {
            "status": status,
            "records_processed": records_processed,
            "records_success": records_success,
            "records_failed": records_failed,
            "duration_seconds": duration_seconds,
            "error_message": error_message
        }
    
    def _log_crawler_task(self, **kwargs):
        """记录爬虫任务日志"""
        try:
            task_log = CrawlerTaskLog(**kwargs)
            self.db.add(task_log)
            self.db.commit()
        except Exception as e:
            logger.error(f"记录任务日志失败: {str(e)}")
            self.db.rollback()
    
    def _record_realtime_metrics(self, source_id: int, status: str, response_time_ms: Optional[float], 
                               records_processed: int, records_failed: int):
        """记录实时指标到监控系统"""
        try:
            # 记录响应时间指标
            if response_time_ms:
                self.alert_service.record_metric(
                    source_id=source_id,
                    metric_type="response_time",
                    metric_value=response_time_ms,
                    tags={"status": status, "timestamp": datetime.utcnow().isoformat()}
                )
            
            # 记录错误计数指标
            if records_failed > 0:
                self.alert_service.record_metric(
                    source_id=source_id,
                    metric_type="error_count",
                    metric_value=float(records_failed),
                    tags={"status": status}
                )
            
            # 记录处理量指标
            if records_processed > 0:
                self.alert_service.record_metric(
                    source_id=source_id,
                    metric_type="processing_rate",
                    metric_value=float(records_processed),
                    tags={"status": status, "duration_minutes": 1}
                )
            
            # 缓存最新的任务状态
            cache_key = f"latest_task_status:{source_id}"
            self.cache.set(cache_key, {
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "response_time_ms": response_time_ms
            }, ttl=300)  # 5分钟缓存
            
        except Exception as e:
            logger.error(f"记录实时指标失败: {str(e)}")
    
    def _update_source_stats(self, source_id: int, status: str, response_time_ms: Optional[float], 
                           records_processed: int):
        """更新数据源统计信息"""
        try:
            from ..models.crawler_source_stats import CrawlerSourceStat
            from ..models.crawler_config import CrawlerConfig
            
            today = datetime.utcnow().date()
            
            # 查找今日统计数据
            stat = self.db.query(CrawlerSourceStat).filter(
                and_(
                    CrawlerSourceStat.source_id == source_id,
                    CrawlerSourceStat.date == today
                )
            ).first()
            
            if not stat:
                # 创建新的统计记录
                source_config = self.db.query(CrawlerConfig).filter(
                    CrawlerConfig.id == source_id
                ).first()
                
                stat = CrawlerSourceStat(
                    source_id=source_id,
                    date=today,
                    source_name=source_config.name if source_config else f"Source_{source_id}"
                )
                self.db.add(stat)
            
            # 更新统计字段
            stat.total_requests += 1
            
            if status == "success":
                stat.successful_requests += 1
                stat.last_success_at = datetime.utcnow()
            else:
                stat.failed_requests += 1
                stat.last_failure_at = datetime.utcnow()
            
            stat.total_records += records_processed
            
            # 更新平均响应时间
            if response_time_ms:
                if stat.avg_response_time_ms:
                    # 计算新的平均值
                    total_prev_requests = stat.successful_requests + stat.failed_requests - 1
                    new_avg = ((stat.avg_response_time_ms * total_prev_requests) + response_time_ms) / (total_prev_requests + 1)
                    stat.avg_response_time_ms = new_avg
                else:
                    stat.avg_response_time_ms = response_time_ms
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"更新数据源统计失败: {str(e)}")
            self.db.rollback()
    
    def _estimate_response_time(self, start_time: datetime) -> Optional[float]:
        """估算响应时间（在实际应用中应该从HTTP客户端获取真实的响应时间）"""
        # 这里返回一个模拟的响应时间
        # 实际应用中应该集成到HTTP请求库中自动捕获
        import random
        return random.uniform(100, 2000)  # 100ms - 2000ms 的随机响应时间
    
    def trigger_manual_alert_check(self):
        """手动触发告警检查"""
        try:
            result = self.alert_service.check_alerts()
            logger.info(f"手动告警检查完成: {result['message']}")
            return result
        except Exception as e:
            logger.error(f"手动告警检查失败: {str(e)}")
            return {"success": False, "message": f"检查失败: {str(e)}"}
    
    def get_source_health_status(self, source_id: Optional[int] = None) -> Dict[str, Any]:
        """获取数据源健康状态"""
        try:
            if source_id:
                # 获取特定数据源的状态
                return self._get_single_source_health(source_id)
            else:
                # 获取所有数据源的状态
                return self._get_all_sources_health()
        except Exception as e:
            logger.error(f"获取数据源健康状态失败: {str(e)}")
            return {"success": False, "message": f"获取状态失败: {str(e)}"}
    
    def _get_single_source_health(self, source_id: int) -> Dict[str, Any]:
        """获取单个数据源健康状态"""
        try:
            # 获取最近24小时的统计数据
            yesterday = datetime.utcnow() - timedelta(hours=24)
            
            logs = self.db.query(CrawlerTaskLog).filter(
                and_(
                    CrawlerTaskLog.source_id == source_id,
                    CrawlerTaskLog.started_at >= yesterday
                )
            ).all()
            
            if not logs:
                return {
                    "source_id": source_id,
                    "status": "unknown",
                    "message": "没有找到执行记录"
                }
            
            total_requests = len(logs)
            failed_requests = len([log for log in logs if log.status == 'failed'])
            success_rate = ((total_requests - failed_requests) / total_requests) * 100
            
            # 计算平均响应时间
            response_times = [log.response_time_ms for log in logs if log.response_time_ms]
            avg_response_time = sum(response_times) / len(response_times) if response_times else None
            
            # 判断健康状态
            if success_rate >= 95:
                status = "healthy"
            elif success_rate >= 80:
                status = "warning"
            else:
                status = "critical"
            
            return {
                "source_id": source_id,
                "status": status,
                "success_rate": round(success_rate, 2),
                "total_requests": total_requests,
                "failed_requests": failed_requests,
                "avg_response_time_ms": round(avg_response_time, 2) if avg_response_time else None,
                "message": f"成功率 {success_rate:.2f}%，平均响应时间 {avg_response_time:.2f}ms" if avg_response_time else f"成功率 {success_rate:.2f}%"
            }
            
        except Exception as e:
            return {
                "source_id": source_id,
                "status": "error",
                "message": f"获取状态失败: {str(e)}"
            }
    
    def _get_all_sources_health(self) -> Dict[str, Any]:
        """获取所有数据源健康状态"""
        try:
            from ..models.crawler_config import CrawlerConfig
            
            sources = self.db.query(CrawlerConfig).filter(
                CrawlerConfig.is_active == True
            ).all()
            
            health_status = {}
            healthy_count = 0
            total_count = len(sources)
            
            for source in sources:
                source_health = self._get_single_source_health(source.id)
                health_status[source.name] = source_health
                
                if source_health["status"] == "healthy":
                    healthy_count += 1
            
            overall_status = "healthy" if healthy_count == total_count else "warning" if healthy_count > total_count * 0.5 else "critical"
            
            return {
                "overall_status": overall_status,
                "total_sources": total_count,
                "healthy_sources": healthy_count,
                "unhealthy_sources": total_count - healthy_count,
                "health_status": health_status
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"获取所有数据源状态失败: {str(e)}"}


def create_enhanced_crawler_service(db: Session) -> EnhancedCrawlerService:
    """创建增强的爬虫服务实例"""
    return EnhancedCrawlerService(db)