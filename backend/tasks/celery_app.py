"""
Celery应用入口模块
"""
from . import celery_app

# 导入任务模块以确保它们被注册到Celery中
from . import match_tasks
from . import intelligence_tasks
from . import crawler_tasks
from . import analytics_tasks
from . import notification_tasks

__all__ = ["celery_app"]