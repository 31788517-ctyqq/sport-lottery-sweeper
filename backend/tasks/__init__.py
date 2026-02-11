"""
任务模块初始化文件
确保所有任务都被正确导入和注册
"""
from celery import Task
from celery import Celery
import os
import sys
from ..core.config import settings

# 创建Celery应用实例
celery_app = Celery(
    'sport_lottery_worker',
    broker=settings.REDIS_URL or 'redis://localhost:6379/0',
    backend=settings.REDIS_URL or 'redis://localhost:6379/0',
    include=[
        'backend.tasks.500wang_scheduler',
        'backend.tasks.agent_tasks',
        'backend.tasks.alert_monitoring_tasks',
        'backend.tasks.analytics_tasks',
        'backend.tasks.crawler_tasks',
        'backend.tasks.crawler_tasks_v2',
        'backend.tasks.draw_prediction_tasks',
        'backend.tasks.intelligence_tasks',
        'backend.tasks.match_tasks',
        'backend.tasks.notification_tasks'
    ]
)

# 配置Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=False,
    result_expires=86400,  # 24小时后结果过期
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    task_time_limit=3600,  # 1小时超时
)


# 数据库任务基类
class DatabaseTask(Task):
    """带数据库连接的任务基类"""
    def __call__(self, *args, **kwargs):
        from backend.database import SessionLocal
        # 创建数据库会话
        db = SessionLocal()
        try:
            # 将数据库会话作为第一个参数传递
            return self.run(db, *args, **kwargs)
        finally:
            # 确保会话被关闭
            db.close()


# 导出DatabaseTask，确保在导入其他模块之前可用
from . import match_tasks
from . import intelligence_tasks
from . import crawler_tasks
from . import analytics_tasks
from . import notification_tasks
from . import alert_monitoring_tasks  # 新增告警监控任务

# 导出所有任务模块的公共接口
__all__ = [
    'match_tasks',
    'intelligence_tasks', 
    'crawler_tasks',
    'analytics_tasks',
    'notification_tasks',
    'alert_monitoring_tasks',  # 新增
    'DatabaseTask',  # 导出DatabaseTask
    'celery_app'     # 导出celery_app
]