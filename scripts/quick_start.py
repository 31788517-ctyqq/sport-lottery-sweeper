"""
快速启动脚本
最小化导入，快速启动服务
"""
import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def quick_create_app():
    """快速创建应用实例，最小化导入"""
    start_time = time.time()
    
    # 只导入必要的模块
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware
    import logging
    
    print(f"[{time.strftime('%H:%M:%S')}] 初始化FastAPI应用...")
    
    # 创建应用实例
    app = FastAPI(
        title="竞彩足球扫盘系统",
        version="0.1.0",
        description="竞彩足球扫盘系统API"
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境中应该限制域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    print(f"[{time.strftime('%H:%M:%S')}] 配置CORS完成")
    
    # 添加基本的日志中间件（精简版）
    @app.middleware("http")
    async def log_requests(request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        request.app.logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.2f}s")
        return response
    
    # 挂载静态文件
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir, exist_ok=True)
    
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    app.mount("/jczq", StaticFiles(directory=static_dir, html=True), name="jczq")
    
    print(f"[{time.strftime('%H:%M:%S')}] 挂载静态文件完成")
    
    # 简单的API路由（避免导入大型模块）
    @app.get("/")
    async def root():
        return {"message": "Sport Lottery Sweeper API - 快速启动模式"}
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "startup_time": time.time() - start_time}
    
    total_time = time.time() - start_time
    print(f"[{time.strftime('%H:%M:%S')}] 应用创建完成，总耗时: {total_time:.3f}s")
    
    return app


if __name__ == "__main__":
    app = quick_create_app()
    
    print("\n启动服务器...")
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8006,
        log_level="info"
    )