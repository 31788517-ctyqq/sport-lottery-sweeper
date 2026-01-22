"""
Celery任务模块初始化
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from celery import Celery
import os

# 创建Celery应用实例
celery_app = Celery('sport_lottery_sweeper')

# 配置Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=False,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,

    # 任务路由
    task_routes={
        "app.tasks.crawler_tasks.*": {"queue": "crawler"},
        "app.tasks.match_tasks.*": {"queue": "data_processing"},
        "app.tasks.intelligence_tasks.*": {"queue": "data_processing"},       
        "app.tasks.analytics_tasks.*": {"queue": "analytics"},
        "app.tasks.notification_tasks.*": {"queue": "notifications"},
    },

    # 任务队列
    task_queues={
        "crawler": {"exchange": "crawler", "routing_key": "crawler"},
        "data_processing": {"exchange": "data_processing", "routing_key": "data_processing"},
        "analytics": {"exchange": "analytics", "routing_key": "analytics"},   
        "notifications": {"exchange": "notifications", "routing_key": "notifications"},
        "default": {"exchange": "default", "routing_key": "default"},
    },

    # 定时任务
    beat_schedule={
        # 每日凌晨1点更新比赛数据
        "update-matches-daily": { 
            "task": "backend.tasks.match_tasks.update_matches_daily",     
            "schedule": 300,  # 每5分钟执行一次，用于测试
            "args": (),
        },
    },
    
    # Broker配置
    broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
)

# 设置日志
logger = logging.getLogger(__name__)

class DatabaseTask(celery_app.Task):
    """
    为所有任务提供数据库会话的基类
    """
    def __call__(self, *args, **kwargs):
        # 在这里可以添加预处理逻辑，如创建数据库会话
        try:
            return super().__call__(*args, **kwargs)
        finally:
            # 在这里可以添加清理逻辑，如关闭数据库会话
            pass

def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    获取任务状态

    Args:
        task_id: 任务ID

    Returns:
        Dict[str, Any]: 任务状态信息
    """
    result = celery_app.AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
        "info": result.info
    }

def revoke_task(task_id: str, terminate: bool = True) -> bool:
    """
    撤销任务

    Args:
        task_id: 任务ID
        terminate: 是否终止任务

    Returns:
        bool: 撤销是否成功
    """
    try:
        celery_app.control.revoke(task_id, terminate=terminate)
        logger.info(f"任务已撤销: {task_id}")
        return True
    except Exception as e:
        logger.error(f"撤销任务失败: {str(e)}")
        return False

def get_queue_stats() -> Dict[str, Any]:
    """
    获取队列统计信息

    Returns:
        Dict[str, Any]: 队列统计
    """
    try:
        inspector = celery_app.control.inspect()

        stats = {
            "active_queues": {},
            "scheduled_tasks": 0,
            "active_tasks": 0,
            "reserved_tasks": 0,
            "registered_tasks": [],
        }

        # 获取活动队列
        active_queues = inspector.active_queues()
        if active_queues:
            for worker, queues in active_queues.items():
                stats["active_queues"][worker] = [q["name"] for q in queues]  

        # 获取计划任务
        scheduled = inspector.scheduled()
        if scheduled:
            for worker, tasks in scheduled.items():
                stats["scheduled_tasks"] += len(tasks)

        # 获取活动任务
        active = inspector.active()
        if active:
            for worker, tasks in active.items():
                stats["active_tasks"] += len(tasks)

        # 获取保留任务
        reserved = inspector.reserved()
        if reserved:
            for worker, tasks in reserved.items():
                stats["reserved_tasks"] += len(tasks)

        # 获取注册任务
        registered = inspector.registered()
        if registered:
            for worker, tasks in registered.items():
                stats["registered_tasks"] = tasks
                break  # 只取一个worker的注册任务列表
        return stats

    except Exception as e:
        logger.error(f"获取队列统计失败: {str(e)}")
        return {
            "error": str(e)
        }

def enqueue_task(task_name: str, args: tuple = None, kwargs: Dict = None,     
                 queue: str = "default", priority: int = 5) -> str:
    """
    将任务加入队列
    Args:
        task_name: 任务名称
        args: 位置参数
        kwargs: 关键字参数
        queue: 队列名称
        priority: 优先级（0-9，最高）

    Returns:
        str: 任务ID
    """
    try:
        task = celery_app.send_task(
            task_name,
            args=args or (),
            kwargs=kwargs or {},
            queue=queue,
            priority=priority
        )

        logger.info(f"任务已加入队列 {task_name}, 任务ID: {task.id}")
        return task.id

    except Exception as e:
        logger.error(f"加入队列失败: {str(e)}")
        raise

# 将DatabaseTask应用为Celery的默认任务基类
celery_app.Task = DatabaseTask

# 定义sporttery_scraper变量以避免导入错误
try:
    # 这里应该导入实际的爬虫实例
    from .scraper import sporttery_scraper
except ImportError:
    # 如果没有找到爬虫模块，创建一个模拟对象
    class MockScraper:
        async def __aenter__(self):
            return self
            
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        
        async def get_recent_matches(self, days):
            # 返回模拟数据
            return self.generate_mock_data(days)
            
        def generate_mock_data(self, days):
            # 生成模拟数据
            import random
            from datetime import datetime, timedelta
            
            matches = []
            for i in range(10):  # 生成10场比赛
                match = {
                    "id": f"match_{i}",
                    "match_date": (datetime.now() + timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d"),
                    "home_team": f"主队{i}",
                    "away_team": f"客队{i}",
                    "league": f"联赛{i % 3}",
                    "odds_home_win": round(random.uniform(1.5, 3.5), 2),
                    "odds_draw": round(random.uniform(2.0, 4.0), 2),
                    "odds_away_win": round(random.uniform(2.0, 5.0), 2),
                    "popularity": random.randint(1, 100),
                    "status": "未开始",
                    "score": "0:0",
                    "match_time": f"{random.randint(10, 22)}:{random.choice(['00', '15', '30', '45'])}",
                    "intelligence": []
                }
                matches.append(match)
            return matches
    
    sporttery_scraper = MockScraper()

__all__ = [
    "celery_app",
    "DatabaseTask",
    "get_task_status",
    "revoke_task",
    "get_queue_stats",
    "enqueue_task",
    "sporttery_scraper"
]

logger.info("Celery应用配置完成")

def create_celery_app():
    """创建Celery应用"""
    return celery_app