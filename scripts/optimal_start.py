"""
最优启动脚本 - 使用最精简配置快速启动
最小化导入，仅包含核心功能，快速启动服务
"""
import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def create_optimized_app():
    """创建优化的应用实例，最小化导入和初始化"""
    start_time = time.time()
    
    # 仅导入必要的模块
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware
    
    print(f"[{time.strftime('%H:%M:%S')}] [T+{time.time()-start_time:.2f}s] 初始化FastAPI应用...")
    
    # 创建应用实例 - 仅包含基本配置
    app = FastAPI(
        title="竞彩足球扫盘系统 - 优化版",
        version="0.1.0",
        description="竞彩足球扫盘系统API - 最优性能版",
        docs_url="/docs",  # 启用文档便于调试
        redoc_url="/redoc"
    )
    
    # 精简CORS配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    print(f"[{time.strftime('%H:%M:%S')}] [T+{time.time()-start_time:.2f}s] 配置CORS完成")
    
    # 精简中间件
    @app.middleware("http")
    async def timing_middleware(request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        response.headers["X-Response-Time"] = str(duration)
        return response
    
    # 静态文件路径
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir, exist_ok=True)
    
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    app.mount("/jczq", StaticFiles(directory=static_dir, html=True), name="jczq")
    
    print(f"[{time.strftime('%H:%M:%S')}] [T+{time.time()-start_time:.2f}s] 挂载静态文件完成")
    
    # 直接定义核心API路由，避免复杂的导入
    @app.get("/")
    async def root():
        return {
            "message": "Sport Lottery Sweeper API - 优化启动版", 
            "startup_time": time.time() - start_time,
            "status": "running"
        }
    
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "uptime": time.time() - start_time
        }
    
    # 添加Jczq路由，这是核心功能
    jczq_router = None
    try:
        # 动态导入竞彩足球API路由
        def get_jczq_router():
            try:
                from backend.api.jczq import router as jczq_router_instance
                return jczq_router_instance
            except ImportError as e:
                print(f"无法导入jczq路由: {e}")
                from fastapi import APIRouter
                router = APIRouter()
                @router.get("/jczq")
                def read_jczq():
                    return {"message": "Jczq API placeholder"}
                return router

        jczq_router_instance = get_jczq_router()
        app.include_router(jczq_router_instance, prefix="")
        print(f"[{time.strftime('%H:%M:%S')}] [T+{time.time()-start_time:.2f}s] Jczq路由加载完成")
    except Exception as e:
        import logging
        logging.warning(f"Jczq路由加载失败: {e}")
        print(f"[{time.strftime('%H:%M:%S')}] [T+{time.time()-start_time:.2f}s] 警告: Jczq路由加载失败")

        # 定义一个简单的替代路由
        @app.get("/api/jczq/matches/recent")
        async def fallback_get_recent_matches(days: int = 3):
            return {
                "status": "error",
                "message": "功能模块暂不可用",
                "fallback": True,
                "requested_days": days
            }
    
    total_time = time.time() - start_time
    print(f"[{time.strftime('%H:%M:%S')}] [T+{total_time:.2f}s] 应用创建完成")
    print(f"\n🚀 服务已准备就绪!")
    print(f"📊 启动耗时: {total_time:.3f}秒")
    print(f"🌍 访问地址: http://127.0.0.1:8009")
    print(f"📋 API文档: http://127.0.0.1:8009/docs")
    print(f"🔍 健康检查: http://127.0.0.1:8009/health")
    
    return app


if __name__ == "__main__":
    app = create_optimized_app()
    
    print("\n⏳ 启动服务器...")
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8009,
        log_level="warning",  # 减少日志输出提高性能
        timeout_keep_alive=30,
        lifespan="off"  # 关闭lifespan以提高性能
    )