"""
FastAPI主应用入口
包含性能优化和时间监测功能
"""
import time
import sys
from contextlib import contextmanager
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from pathlib import Path

# 动态添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入数据库模块以确保表被创建
from backend.database import engine

# 添加项目用户管理路由
from backend.config import settings
from backend.core.middleware import RequestLoggingMiddleware
from backend.core.async_initializer import get_async_initializer
from backend.utils.logging_config import setup_logging, shutdown_logging

@contextmanager
def timer(name: str):
    """计时上下文管理器"""
    start = time.perf_counter()
    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] 开始: {name}")
    yield
    elapsed = time.perf_counter() - start
    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] 完成: {name} (耗时: {elapsed:.3f}s)")


# 配置日志
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时执行
    startup_start = time.time()
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 开始启动应用...")

    with timer("异步初始化关键服务"):
        initializer = get_async_initializer()
        await initializer.initialize_all()

    startup_total = time.time() - startup_start
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 应用启动完成，总耗时: {startup_total:.3f}s")

    yield

    # 关闭时执行
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 关闭应用...")
    shutdown_logging()


def create_app() -> FastAPI:
    """创建优化的FastAPI应用实例"""
    app_start = time.time()

    with timer("创建FastAPI应用实例"):
        app = FastAPI(
            title=settings.PROJECT_NAME,
            version=settings.VERSION,
            description=settings.DESCRIPTION,
            openapi_url=f"{settings.API_V1_STR}/openapi.json",
            docs_url="/docs" if settings.DOCS_ENABLED else None,
            redoc_url="/redoc" if settings.DOCS_ENABLED else None,
            lifespan=lifespan
        )

    with timer("配置CORS中间件"):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    with timer("添加自定义中间件"):
        app.add_middleware(RequestLoggingMiddleware)

    with timer("包含API路由"):
        from backend.api.v1 import create_api_router
        api_v1_router = create_api_router()
        app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    # 延迟导入管理后台路由，避免循环导入问题
    with timer("添加根路径路由"):
        @app.get("/")
        async def root():
            startup_time = time.time() - app_start
            return {
                "message": "Welcome to Sport Lottery Sweeper API",
                "version": settings.VERSION,
                "startup_time": f"{startup_time:.3f}s",
                "docs": f"{settings.API_V1_STR}/docs" if settings.DOCS_ENABLED else None,
                "timestamp": datetime.now().isoformat()
            }

    app_total = time.time() - app_start
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 应用构建完成，总耗时: {app_total:.3f}s")

    return app


# 创建应用实例
app = create_app()

# 在应用启动后注册管理后台路由（避免循环导入）
@app.on_event("startup")
async def register_admin_routes():
    """在应用启动后注册管理后台路由"""
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 开始注册管理后台路由...")
    from backend.admin import admin_router
    app.include_router(admin_router)
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 管理后台路由注册完成")

import asyncio

@app.websocket("/ws/matches")
async def websocket_matches(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time()
    }


if __name__ == "__main__":
    import uvicorn
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 启动Uvicorn服务器...")

    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )