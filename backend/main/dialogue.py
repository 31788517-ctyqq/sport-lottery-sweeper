@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Application starting up...")
    
    # 初始化日志系统
    from backend.utils.logging_config import setup_logging
    setup_logging()
    
    # 初始化数据库
    from backend.database import engine, Base
    Base.metadata.create_all(bind=engine)
    
    # 暂时禁用启动时的数据源同步，避免ORM冲突
    # sync_data_source_to_crawler_config()
    
    # 初始化各种服务
    # initialize_services()  # 暂时注释掉未定义的函数调用
    
    yield
    
    # 应用关闭时的清理
    logger.info("Application shutting down...")
