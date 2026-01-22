"""
任务模块初始化文件
确保所有任务都被正确导入和注册
"""
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
    'alert_monitoring_tasks'  # 新增
]