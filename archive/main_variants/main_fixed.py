#!/usr/bin/env python3
"""
体育彩票扫盘系统 - 主应用入口
真实数据库版本
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根目录
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.v1 import auth, admin, matches, lottery, intelligence, frontend_user_management, sp_management, draw_prediction
from core.config import settings
from database import engine, Base
from .models.user import User

# 导入中间件
from middleware.request_logging import RequestLoggingMiddleware
from middleware.security_headers import SecurityHeadersMiddleware
from middleware.rate_limit import RateLimitMiddleware

# 导入监控
from monitoring.performance_monitor import PerformanceMonitor
from monitoring.error_tracker import ErrorTracker

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="体育彩票扫盘分析系统 - 真实数据库版本",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# 性能监控器
perf_monitor = PerformanceMonitor()
error_tracker = ErrorTracker()

# 中间件（按顺序执行）
# 1. 安全头中间件
app.add_middleware(SecurityHeadersMiddleware)

# 2. 请求日志中间件
app.add_middleware(RequestLoggingMiddleware)

# 3. 限流中间件
app.add_middleware(
    RateLimitMiddleware,
    max_requests_per_minute=settings.RATE_LIMIT_PER_MINUTE
)

# 4. CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 事件处理器
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    print("🚀 正在启动体育彩票扫盘系统...")
    
    # 创建数据库表
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建/检查完成")
    except Exception as e:
        print(f"❌ 数据库表创建失败: {e}")
        # 不阻断启动，允许后续处理
    
    # 初始化监控
    perf_monitor.start_monitoring()
    print("✅ 性能监控已启动")
    
    print(f"✅ {settings.PROJECT_NAME} v{settings.VERSION} 启动完成")
    print(f"📖 API文档: http://localhost:8000/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    print("🛑 正在关闭体育彩票扫盘系统...")
    perf_monitor.stop_monitoring()
    print("✅ 系统已安全关闭")

# 根路径重定向到API文档
@app.get("/")
async def root():
    return {
        "message": f"欢迎使用 {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
        "api_prefix": "/api/v1"
    }

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": settings.VERSION
    }

# 包含API路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["administration"])
app.include_router(matches.router, prefix="/api/v1/matches", tags=["matches"])
app.include_router(lottery.router, prefix="/api/v1/lottery", tags=["lottery"])
app.include_router(intelligence.router, prefix="/api/v1/intelligence", tags=["intelligence"])
app.include_router(frontend_user_management.router, prefix="/api/v1/users", tags=["frontend-users"])
app.include_router(sp_management.router, prefix="/api/v1/sp", tags=["sp-management"])
app.include_router(draw_prediction.router, prefix="/api/v1/draw", tags=["draw-prediction"])

    # 直接注册系统管理路由（日志、健康检查）
try:
        from backend.app.api.admin.system.health import router as health_router
        app.include_router(health_router, prefix="/api/v1/admin/system", tags=["system-health"])
        print("[INFO] 系统健康检查路由已注册")
except Exception as e:
        print(f"[ERROR] API v1 - admin system health 路由注册失败: {str(e)}")

try:
        from backend.app.api.admin.system.logs import router as logs_router
        app.include_router(logs_router, prefix="/api/v1/admin/system", tags=["system-logs"])
        print("[INFO] 系统日志路由已注册")
except Exception as e:
        print(f"[ERROR] API v1 - admin system logs 路由注册失败: {str(e)}")

# 静态文件服务（用于上传的文件）
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )