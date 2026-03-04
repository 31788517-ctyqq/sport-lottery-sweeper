"""
FastAPI主应用入口 - 生产环境优化版（禁用热重载）
适用于生产环境或不需要热重载的开发场景，使用自定义端口
"""
import time
import sys
import os
from contextlib import contextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# 添加项目根目录到Python路径，以确保模块可以正确导入
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from backend.config import settings


@contextmanager
def timer(name: str):
    """计时上下文管理器"""
    start = time.perf_counter()
    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] 🚀 开始: {name}")
    yield
    elapsed = time.perf_counter() - start
    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] ✅ 完成: {name} (耗时: {elapsed:.3f}s)")


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时执行 - 最小化初始化
    startup_start = time.time()
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 🌟 开始启动应用...")

    startup_total = time.time() - startup_start
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 🎉 应用启动完成，总耗时: {startup_total:.3f}s")

    yield

    # 关闭时执行
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 💤 关闭应用...")


def create_app() -> FastAPI:
    """创建优化的FastAPI应用实例，最小化启动耗时"""
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

    with timer("包含API路由"):
        from backend.api import router
        app.include_router(router, prefix=settings.API_V1_STR)

    with timer("包含管理后台路由"):
        from backend.admin import admin_router
        app.include_router(admin_router)

    with timer("添加根路径路由"):
        @app.get("/")
        async def root():
            startup_time = time.time() - app_start
            return {
                "message": "Welcome to Sport Lottery Sweeper API",
                "startup_time": f"{startup_time:.3f}s",
                "timestamp": datetime.now().isoformat()
            }

    app_total = time.time() - app_start
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 🏗️  应用构建完成，总耗时: {app_total:.3f}s")

    return app


# 创建应用实例
app = create_app()


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
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 🚀 启动Uvicorn服务器...")

    # 不启用热重载(reload=False)，适合生产环境，使用端口8002
    uvicorn.run(
        "backend.production_main:app",
        host=settings.HOST,
        port=8002,  # 使用端口8002
        reload=False,  # 禁用热重载功能
        log_level="info"
    )