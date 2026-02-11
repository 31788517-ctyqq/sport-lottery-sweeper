#!/usr/bin/env python3
"""
体育彩票扫盘系统 - 主应用入口（简化版）
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import sys

# 设置项目路径
current_file = os.path.abspath(__file__)
backend_dir = os.path.dirname(current_file)
project_root = os.path.dirname(backend_dir)

sys.path.insert(0, project_root)

app = FastAPI(
    title="体育彩票扫盘系统",
    description="Sports Lottery Sweeper API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 引入认证路由
try:
    from api.v1.simple_auth import router as auth_router
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
    print("✅ Simple Auth routes loaded successfully")
except ImportError as e:
    print(f"❌ Could not import simple auth routes: {e}")

# CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 基础路由
@app.get("/")
async def root():
    return {"message": "体育彩票扫盘系统 API", "version": "1.0.0"}

@app.get("/health/live")
async def health_live():
    return {"status": "healthy", "service": "sport-lottery-sweeper"}

@app.get("/health/ready")
async def health_ready():
    return {"status": "ready", "database": "connected", "cache": "connected"}

@app.get("/api/v1/health")
async def api_health():
    return {"code": 200, "message": "API服务正常", "data": {"timestamp": datetime.now().isoformat()}}

if __name__ == "__main__":
    import uvicorn
    print("🚀 启动体育彩票扫盘系统...")
    uvicorn.run("main_simple:app", host="0.0.0.0", port=8000, reload=True)