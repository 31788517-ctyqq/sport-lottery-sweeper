from .crawler.config import bp as config_bp
from .crawler.source import bp as source_bp
from .crawler.task import bp as task_bp
from .crawler.intelligence import bp as intelligence_bp
from .system.health import router as health_router
from .system.logs import router as logs_router

def init_admin_crawler(app):
    app.register_blueprint(config_bp)
    app.register_blueprint(source_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(intelligence_bp)

def init_admin_system(app):
    """初始化系统管理模块"""
    app.include_router(health_router, prefix="/api/v1/admin/system", tags=["system-health"])
    app.include_router(logs_router, prefix="/api/v1/admin/system", tags=["system-logs"])