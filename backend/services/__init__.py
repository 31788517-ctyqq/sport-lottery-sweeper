"""
业务服务模块导出
"""
from .auth_service import (
    AuthenticationService,
    TokenService,
    PermissionService,
    UserManagementService
)
from .match_service import MatchService
from .intelligence_service import IntelligenceService
from .crawler_config_service import CrawlerService
from .notification_service import NotificationService
from .analytics_service import AnalyticsService

# 服务实例
__all__ = [
    "AuthenticationService",
    "TokenService", 
    "PermissionService",
    "UserManagementService",
    "MatchService",
    "IntelligenceService", 
    "CrawlerService",
    "NotificationService",
    "AnalyticsService"
]

# 服务容器（用于依赖注入）
class ServiceContainer:
    """服务容器，用于管理服务实例"""
    
    def __init__(self):
        self._services = {}
    
    def register(self, name: str, service):
        """注册服务"""
        self._services[name] = service
    
    def get(self, name: str):
        """获取服务"""
        return self._services.get(name)
    
    def __getitem__(self, name: str):
        return self.get(name)

# 创建全局服务容器
services = ServiceContainer()