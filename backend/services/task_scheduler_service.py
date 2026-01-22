"""
任务调度服务
处理爬虫任务的创建、调度和执行管理
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import uuid

from ..models.crawler_config import CrawlerConfig
from ..models.crawler_tasks import CrawlerTask
from ..models.crawler_logs import CrawlerTaskLog
from ..models.admin_user import AdminUser
from ..schemas.crawler import (
    CrawlerTaskCreate, CrawlerTaskUpdate, CrawlerTaskResponse
)
from .crawler_service import BaseCrawlerService


class TaskSchedulerService(BaseCrawlerService):
    """任务调度服务类"""
    
    def get_tasks(self, status: Optional[str] = None, source_id: Optional[int] = None,
                  page: int = 1, page_size: int = 20) -> List[CrawlerTaskResponse]:
        """
        获取任务列表
        
        Args:
            status: 状态筛选
            source_id: 数据源ID筛选
            page: 页码
            page_size: 每页数量
            
        Returns:
            List[CrawlerTaskResponse]: 任务列表
        """
        query = self.db.query(CrawlerTask)
        
        # 状态筛选
        if status:
            query = query.filter(CrawlerTask.status == status)
        
        # 数据源筛选
        if source_id:
            query = query.filter(CrawlerTask.source_id == source_id)
        
        # 分页
        offset = (page - 1) * page_size
        tasks = query.order_by(desc(CrawlerTask.updated_at)).offset(offset).limit(page_size).all()
        
        # 转换为响应模型（已经是真实数据，无需模拟）
        result = []
        for task in tasks:
            # 获取关联的数据源信息
            source = self.db.query(CrawlerConfig).filter(
                CrawlerConfig.id == task.source_id
            ).first()
            
            # 如果有最后运行时间，计算下次运行时间
            next_run_time = None
            if task.last_run_time and task.cron_expression and task.is_active:
                # 这里简化处理：基于cron表达式和最后运行时间计算
                # 实际应用中应使用cron解析库如croniter
                next_run_time = task.last_run_time + timedelta(hours=1)
            
            response = CrawlerTaskResponse(
                id=task.id,
                name=task.name,
                source_id=task.source_id,
                task_type=task.task_type,
                cron_expression=task.cron_expression,
                is_active=task.is_active,
                status=task.status,
                last_run_time=task.last_run_time,
                next_run_time=next_run_time,
                run_count=task.run_count,
                success_count=task.success_count,
                error_count=task.error_count,
                config=task.config or {"timeout": 30, "retry": 3},
                created_at=task.created_at,
                updated_at=task.updated_at
            )
            
            # 状态二次筛选（确保状态筛选生效）
            if status and response.status != status:
                continue
                
            result.append(response)
        
        return result
    
    def create_task(self, task_data: CrawlerTaskCreate, created_by: int) -> CrawlerTaskResponse:
        """
        创建爬虫任务
        
        Args:
            task_data: 任务创建数据
            created_by: 创建者ID
            
        Returns:
            CrawlerTaskResponse: 创建的任务
        """
        # 检查数据源是否存在
        source = self.db.query(CrawlerConfig).filter(
            CrawlerConfig.id == task_data.source_id
        ).first()
        
        if not source:
            raise ValueError("数据源不存在")
        
        # 验证Cron表达式（简单验证）
        if not self._validate_cron_expression(task_data.cron_expression):
            raise ValueError("无效的Cron表达式")
        
        # 模拟创建任务
        import hashlib
        task_id = int(hashlib.md5(
            f"{task_data.source_id}{task_data.task_type}{self._get_current_timestamp()}".encode()
        ).hexdigest()[:8], 16) % 100000
        
        now = datetime.utcnow()
        
        return CrawlerTaskResponse(
            id=task_id,
            name=task_data.name,
            source_id=task_data.source_id,
            task_type=task_data.task_type,
            cron_expression=task_data.cron_expression,
            is_active=task_data.is_active,
            status="stopped" if not task_data.is_active else "running",
            last_run_time=None,
            next_run_time=now + timedelta(minutes=1) if task_data.is_active else None,
            run_count=0,
            success_count=0,
            error_count=0,
            config=task_data.config or {},
            created_at=now,
            updated_at=now
        )
    
    def update_task_status(self, task_id: int, new_status: str, updated_by: int) -> bool:
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            new_status: 新状态
            updated_by: 更新者ID
            
        Returns:
            bool: 是否更新成功
        """
        # 模拟更新任务状态
        # 在实际应用中，这里应该更新Task表
        valid_statuses = ["running", "stopped", "error", "completed"]
        if new_status not in valid_statuses:
            return False
        
        # 这里应该更新数据库中的任务状态
        # 现在只是模拟返回成功
        return True
    
    def trigger_task(self, task_id: int, triggered_by: int) -> Dict[str, Any]:
        """
        手动触发任务执行
        
        Args:
            task_id: 任务ID
            triggered_by: 触发者ID
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        # 模拟任务执行
        import random
        import time
        
        start_time = time.time()
        
        # 模拟任务执行时间
        execution_time = random.uniform(0.5, 3.0)
        time.sleep(min(execution_time, 1.0))  # 最多等待1秒
        
        # 模拟执行结果
        success = random.choice([True, True, True, False])  # 75%成功率
        items_processed = random.randint(10, 100)
        
        return {
            "task_id": task_id,
            "status": "success" if success else "error",
            "execution_time": round(time.time() - start_time, 2),
            "items_processed": items_processed,
            "success": success,
            "message": f"任务执行{'成功' if success else '失败'}，处理了{items_processed}条数据",
            "triggered_by": triggered_by,
            "timestamp": self._get_current_timestamp()
        }
    
    def get_task_logs(self, task_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取任务执行日志
        
        Args:
            task_id: 任务ID
            limit: 日志条数限制
            
        Returns:
            List[Dict[str, Any]]: 日志列表
        """
        # 模拟日志数据
        logs = []
        base_time = datetime.utcnow()
        
        for i in range(min(limit, 20)):  # 最多生成20条日志
            log_time = base_time - timedelta(minutes=i * 30)
            status = random.choice(["success", "error", "warning"])
            
            log_entry = {
                "id": i + 1,
                "task_id": task_id,
                "status": status,
                "message": self._generate_log_message(status, task_id),
                "execution_time": round(random.uniform(0.5, 5.0), 2),
                "items_processed": random.randint(5, 50),
                "timestamp": log_time.isoformat(),
                "details": {
                    "memory_usage": f"{random.randint(50, 200)}MB",
                    "cpu_usage": f"{random.randint(10, 80)}%"
                }
            }
            logs.append(log_entry)
        
        return sorted(logs, key=lambda x: x["timestamp"], reverse=True)
    
    def _validate_cron_expression(self, cron_expr: str) -> bool:
        """
        验证Cron表达式（简单验证）
        
        Args:
            cron_expr: Cron表达式
            
        Returns:
            bool: 是否有效
        """
        if not cron_expr:
            return False
        
        parts = cron_expr.split()
        # 简单的5位或6位Cron表达式验证
        if len(parts) < 5 or len(parts) > 6:
            return False
        
        # 检查基本格式（更严格的验证需要使用专门的库如croniter）
        return all(part.strip() for part in parts)
    
    def _generate_log_message(self, status: str, task_id: int) -> str:
        """
        生成日志消息
        
        Args:
            status: 状态
            task_id: 任务ID
            
        Returns:
            str: 日志消息
        """
        messages = {
            "success": [
                f"任务 {task_id} 执行成功，数据抓取完成",
                f"任务 {task_id} 正常运行，未发现异常",
                f"任务 {task_id} 数据采集成功，质量良好"
            ],
            "error": [
                f"任务 {task_id} 执行失败，网络连接超时",
                f"任务 {task_id} 数据源返回错误状态码",
                f"任务 {task_id} 解析数据时发生异常"
            ],
            "warning": [
                f"任务 {task_id} 部分数据格式异常，已跳过",
                f"任务 {task_id} 响应时间过长，建议优化",
                f"任务 {task_id} 数据源返回数据不完整"
            ]
        }
        
        import random
        return random.choice(messages.get(status, ["未知状态"]))
    
    def calculate_next_run_time(self, cron_expression: str, last_run: datetime) -> datetime:
        """
        计算下次运行时间
        
        Args:
            cron_expression: Cron表达式
            last_run: 上次运行时间
            
        Returns:
            datetime: 下次运行时间
        """
        # 简化实现：基于Cron表达式的简单计算
        # 实际应用中应使用croniter等专业库
        
        if "* * * *" in cron_expression:  # 每分钟
            return last_run + timedelta(minutes=1)
        elif "0 * * * *" in cron_expression:  # 每小时
            return last_run + timedelta(hours=1)
        elif "0 0 * * *" in cron_expression:  # 每天
            return last_run + timedelta(days=1)
        elif "0 0 * * 0" in cron_expression:  # 每周
            return last_run + timedelta(weeks=1)
        else:
            # 默认1小时后
            return last_run + timedelta(hours=1)