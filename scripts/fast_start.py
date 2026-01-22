"""
快速启动脚本 - 使用精简API
最小化导入，只包含核心功能，快速启动服务
"""
import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def fast_create_app():
    """快速创建应用实例，最小化导入"""
    start_time = time.time()
    
    # 只导入必要的模块
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware
    import logging
    
    print(f"[{time.strftime('%H:%M:%S')}] [{(time.time()-start_time):.2f}s] 初始化FastAPI应用...")
    
    # 创建应用实例
    app = FastAPI(
        title="竞彩足球扫盘系统 - 快速启动版",
        version="0.1.0",
        description="竞彩足球扫盘系统API - 精简版"
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境中应该限制域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    print(f"[{time.strftime('%H:%M:%S')}] [{(time.time()-start_time):.2f}s] 配置CORS完成")
    
    # 添加简单的日志中间件
    @app.middleware("http")
    async def log_requests(request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        print(f"{request.method} {request.url} - {response.status_code} - {process_time:.2f}s")
        return response
    
    # 挂载静态文件
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir, exist_ok=True)
    
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    app.mount("/jczq", StaticFiles(directory=static_dir, html=True), name="jczq")
    
    print(f"[{time.strftime('%H:%M:%S')}] [{(time.time()-start_time):.2f}s] 挂载静态文件完成")
    
    # 包含最小化API路由
    def get_minimal_api_router():
        # 动态导入最小API路由
        try:
            from backend.api.minimal_api import minimal_router
            return minimal_router
        except ImportError as e:
            print(f"无法导入minimal_api: {e}")
            # 如果导入失败，返回一个简单的路由
            from fastapi import APIRouter
            router = APIRouter()
            @router.get("/")
            def read_root():
                return {"message": "Minimal API is running"}
            return router
    
    app.include_router(get_minimal_api_router(), prefix="/api")
    
    print(f"[{time.strftime('%H:%M:%S')}] [{(time.time()-start_time):.2f}s] 包含API路由完成")
    
    # 根路径路由
    @app.get("/")
    async def root():
        return {"message": "Sport Lottery Sweeper API - 快速启动模式", "startup_time": time.time() - start_time}
    
    total_time = time.time() - start_time
    print(f"[{time.strftime('%H:%M:%S')}] [{total_time:.2f}s] 应用创建完成")
    
    return app


if __name__ == "__main__":
    app = fast_create_app()
    
    print("\n启动服务器...")
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8008,
        log_level="info"
    )