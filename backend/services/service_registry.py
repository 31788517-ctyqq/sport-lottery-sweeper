"""
服务注册表 - 解决循环依赖问题
"""

from .crawler_config_service import CrawlerConfigService
from .crawler_integration import CrawlerIntegrationService
from .enhanced_crawler_service import EnhancedCrawlerService
from .crawler_alert_service import CrawlerAlertService

# 服务实例缓存
_service_cache = {}

def get_data_source_service(db):
    """获取数据源服务"""
    key = f"datasource_{id(db)}"
    if key not in _service_cache:
        _service_cache[key] = CrawlerConfigService(db)
    return _service_cache[key]

def get_task_scheduler_service(db):
    """获取任务调度服务"""
    key = f"taskscheduler_{id(db)}"
    if key not in _service_cache:
        _service_cache[key] = CrawlerIntegrationService()
    return _service_cache[key]

def get_intelligence_service(db):
    """获取情报服务"""
    key = f"intelligence_{id(db)}"
    if key not in _service_cache:
        _service_cache[key] = EnhancedCrawlerService(db)
    return _service_cache[key]

def get_alert_service(db):
    """获取告警服务"""
    key = f"alert_{id(db)}"
    if key not in _service_cache:
        _service_cache[key] = CrawlerAlertService(db)
    return _service_cache[key]