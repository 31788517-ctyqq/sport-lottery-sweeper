#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动后端服务
最小化启动，跳过不必要的初始化
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

# 加载 .env 文件
from dotenv import load_dotenv
load_dotenv()

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 设置最低级别的日志，减少日志输出
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 导入必要的数据库工具
from backend.database_utils import authenticate_user, get_user_by_id

from contextlib import asynccontextmanager

def create_minimal_app():
    """创建最小化的FastAPI应用"""
    # 创建FastAPI应用
    app = FastAPI(
        title="体育彩票扫盘系统 - 快速启动模式",
        description="Sports Lottery Sweeper API - 最小化启动",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 仅添加最基本的CORS中间件
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
        return {"message": "体育彩票扫盘系统 API - 快速启动模式", "version": "1.0.0"}

    @app.get("/health/live")
    async def health_live():
        return {"status": "healthy", "service": "sport-lottery-sweeper"}

    @app.get("/health/ready")
    async def health_ready():
        # 检查数据库连接
        try:
            from backend.database_utils import get_db_connection
            conn = get_db_connection()
            conn.close()
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return {"status": "ready", "database": db_status}

    # 登录相关路由
    from fastapi import Body
    import jwt
    from datetime import datetime as dt, timezone, timedelta

    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-test-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 7200  # 2小时

    def create_access_token(data: dict):
        """创建JWT访问令牌"""
        to_encode = data.copy()
        expire = dt.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @app.post("/api/v1/auth/login")
    async def login_v1(username: str = Body(...), password: str = Body(...)):
        """用户登录接口 - 真实数据库验证"""
        logger.info(f"Login attempt for username: {username}")
        user = authenticate_user(username, password)
        if not user:
            logger.warning(f"Login failed: invalid credentials for username {username}")
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        
        logger.info(f"User logged in successfully: {user['username']} (ID: {user['id']})")
        
        # 创建JWT令牌
        access_token = create_access_token({
            "user_id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"]
        })
        
        return {
            "code": 200,
            "message": "登录成功",
            "data": {
                "access_token": access_token,
                "refresh_token": f"refresh-{access_token}",
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user_info": {
                    "userId": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "roles": [user["role"]],
                    "status": user["status"]
                }
            }
        }

    # 仅注册核心的API路由，跳过多余的模块
    try:
        # 导入并注册管理API路由
        from backend.api.v1.admin import router as admin_router
        app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
        logger.info("Admin API路由已注册")
    except Exception as e:
        logger.error(f"Admin API路由注册失败: {e}")

    try:
        # 导入并注册彩票相关路由
        from backend.api.v1.lottery import router as lottery_router
        app.include_router(lottery_router, prefix="/api/v1/lottery", tags=["lottery"])
        logger.info("Lottery API路由已注册")
    except Exception as e:
        logger.error(f"Lottery API路由注册失败: {e}")

    try:
        # 导入并注册对冲相关路由
        from backend.api.v1.hedging import router as hedging_router
        app.include_router(hedging_router, prefix="/api/v1/hedging", tags=["hedging"])
        logger.info("Hedging API路由已注册")
    except Exception as e:
        logger.error(f"Hedging API路由注册失败: {e}")

    return app

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser(description='Fast Backend Server')
    parser.add_argument('--port', type=int, default=8002, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the server on')
    args = parser.parse_args()
    
    app = create_minimal_app()
    
    print(f"Starting fast backend server on {args.host}:{args.port}")
    print("Minimal services enabled for faster startup")
    uvicorn.run(app, host=args.host, port=args.port, reload=False, log_level="error")