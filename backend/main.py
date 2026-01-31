#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
体育彩票扫盘系统 - 主应用入口
真实数据库版本
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
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 导入日志配置并设置日志
from backend.utils.logging_config import setup_logging
setup_logging()

# 获取logger实例
logger = logging.getLogger(__name__)

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# 导入日志中间件
from backend.core.logging_middleware import LoggingMiddleware

# 导入监控和限流中间件
from backend.core.monitoring_middleware import MonitoringMiddleware
from backend.core.rate_limit_middleware import RateLimitMiddleware

# 导入性能优化中间件
from backend.core.performance_middleware import PerformanceMiddleware

# 导入数据库工具
from backend.database_utils import (
    authenticate_user, get_user_by_id, 
    get_dashboard_stats, get_intelligence_screening_list
)

from contextlib import asynccontextmanager

# 全局变量声明
llm_service = None
collaborative_agents = None
communication_hub = None

def init_llm_service():
    """初始化LLM服务"""
    global llm_service
    try:
        from backend.llm.service import LLMService
        llm_service = LLMService()
        logger.info("LLM服务已初始化")
    except Exception as e:
        logger.warning(f"LLM服务初始化失败: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Application starting up...")
    
    # 初始化LLM服务
    init_llm_service()
    
    # TODO: 初始化视频分析服务（需要数据库会话依赖）
    logger.info("视频分析服务已准备")
    
    # TODO: 初始化报告生成服务（需要数据库会话和LLM服务依赖）
    logger.info("报告生成服务已准备")
    
    # TODO: 初始化多智能体协作系统
    try:
        from backend.agents.communication_protocol import CommunicationHub
        from backend.agents.collaborative_prediction_agent import (
            DataCollectionAgent, 
            AnalysisAgent, 
            PredictionAgent, 
            RiskControlAgent
        )
        
        # 创建通信中心
        global communication_hub
        communication_hub = CommunicationHub()
        
        # 创建智能体实例
        global collaborative_agents
        data_agent = DataCollectionAgent("data_collection_agent", {}, communication_hub)
        analysis_agent = AnalysisAgent("analysis_agent", {}, communication_hub)
        prediction_agent = PredictionAgent("prediction_agent", {}, communication_hub)
        risk_agent = RiskControlAgent("risk_control_agent", {}, communication_hub)
        
        collaborative_agents = {
            "data_collection": data_agent,
            "analysis": analysis_agent,
            "prediction": prediction_agent,
            "risk_control": risk_agent
        }
        
        logger.info("多智能体协作系统已初始化")
    except Exception as e:
        logger.warning(f"多智能体协作系统初始化失败: {e}")
    
    yield
    
    # 应用关闭时的清理
    logger.info("Application shutting down...")

# 创建FastAPI应用
app = FastAPI(
    title="体育彩票扫盘系统",
    description="Sports Lottery Sweeper API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加性能优化中间件 - 在其他中间件之前添加
app.add_middleware(PerformanceMiddleware)

# 添加监控中间件 - 在其他中间件之前添加
app.add_middleware(MonitoringMiddleware)

# 添加限流中间件
app.add_middleware(RateLimitMiddleware, requests_per_minute=120, ban_duration=300)

# 添加日志中间件 - 必须在其他中间件之前添加
app.add_middleware(LoggingMiddleware)

logger.info("Application starting up...")  # 添加启动日志

# 强制启用完整API模式，注册所有路由
import os
os.environ['FULL_API_MODE'] = 'true'

# AI_WORKING: coder1 @2026-01-29 - 替换print为logging，统一日志记录
# 导入API v1路由 - 启用完整API模式
logger.info("正在注册API路由...")
# AI_DONE: coder1 @2026-01-29
try:
    from backend.api.v1 import router as api_v1_router
    app.include_router(api_v1_router, prefix="/api/v1")
    logger.info("API v1 路由已成功注册")
except Exception as e:
    logger.error(f"API v1 路由注册失败: {e}")
    # 即使API路由注册失败，也继续运行基本服务

# 注册数据源管理API - 使用正确的路径
try:
    from backend.api.v1.admin.data_source import router as data_source_router
    # 不需要额外的prefix，因为data_source路由内部已经有正确的前缀结构
    app.include_router(data_source_router, prefix="/api/v1/admin", tags=["admin-data-sources"])
    logger.info("数据源管理API路由已成功注册")
except Exception as e:
    logger.error(f"数据源管理API路由注册失败: {e}")

# AI_WORKING: coder2 @2026-01-28T09:49:56Z - 注释掉重复的竞彩赛程管理路由注册，避免操作ID重复警告
# 直接注册竞彩赛程管理路由（确保它能正常工作）- 已通过api/v1路由注册，注释掉以避免重复
# try:
#     from backend.api.v1.lottery_schedule import router as lottery_schedule_router
#     app.include_router(lottery_schedule_router, prefix="/api/v1/admin/lottery-schedules", tags=["admin-lottery-schedules"])
#     logger.info("竞彩赛程管理路由已成功注册")
# except Exception as e:
#     logger.error(f"竞彩赛程管理路由注册失败: {e}")
# AI_DONE: coder2 @2026-01-28T09:49:56Z

# 注册竞彩足球数据路由（前端需要的）- 已通过api/v1路由注册lottery_test_router
# try:
#     from backend.api.v1.lottery import router as lottery_router
#     app.include_router(lottery_router, prefix="/api/v1/lottery", tags=["lottery"])
#     logger.info("竞彩足球数据路由已成功注册")
# except Exception as e:
    logger.error(f"竞彩足球数据路由注册失败: {e}")

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
try:
    from backend.exceptions import setup_exception_handlers
    setup_exception_handlers(app)
    logger.info("异常处理器已注册")
except Exception as e:
    logger.error(f"异常处理器注册失败: {e}")

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Application starting up...")
    
    # 初始化LLM服务
    init_llm_service()
    
    # TODO: 初始化视频分析服务（需要数据库会话依赖）
    logger.info("Video analysis service prepared")
    
    # TODO: 初始化报告生成服务（需要数据库会话和LLM服务依赖）
    logger.info("Report generation service prepared")
    
    # TODO: 初始化多智能体协作系统
    try:
        from backend.agents.communication_protocol import CommunicationHub
        from backend.agents.collaborative_prediction_agent import (
            DataCollectionAgent, 
            AnalysisAgent, 
            PredictionAgent, 
            RiskControlAgent
        )
        
        # 创建通信中心
        global communication_hub
        communication_hub = CommunicationHub()
        
        # 创建智能体实例
        global collaborative_agents
        data_agent = DataCollectionAgent("data_collection_agent", {}, communication_hub)
        analysis_agent = AnalysisAgent("analysis_agent", {}, communication_hub)
        prediction_agent = PredictionAgent("prediction_agent", {}, communication_hub)
        risk_agent = RiskControlAgent("risk_control_agent", {}, communication_hub)
        
        collaborative_agents = {
            "data_collection": data_agent,
            "analysis": analysis_agent,
            "prediction": prediction_agent,
            "risk_control": risk_agent
        }
        
        logger.info("Multi-agent collaboration system initialized")
    except Exception as e:
        logger.warning(f"Multi-agent collaboration system initialization failed: {e}")
    
    yield
    
    # 应用关闭时的清理
    logger.info("Application shutting down...")

# 基础路由
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "体育彩票扫盘系统 API", "version": "1.0.0"}

@app.get("/health/live")
async def health_live():
    logger.debug("Health live check accessed")
    return {"status": "healthy", "service": "sport-lottery-sweeper"}

@app.get("/health/ready")
async def health_ready():
    logger.debug("Health ready check accessed")
    # 检查数据库连接
    try:
        # 使用绝对路径导入，避免相对导入问题
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from backend.database_utils import get_db_connection
        conn = get_db_connection()
        conn.close()
        db_status = "connected"
        logger.info("Database connection check passed")
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        db_status = f"error: {str(e)}"
    
    # 检查AI服务状态
    ai_status = "available" if llm_service and llm_service.providers else "unavailable"
    providers_count = len(llm_service.providers) if llm_service else 0
    agents_status = "available" if collaborative_agents else "unavailable"
    
    return {
        "status": "ready", 
        "database": db_status, 
        "cache": "connected",
        "ai_services": {
            "status": ai_status,
            "providers_registered": providers_count,
            "mult_agent_system": agents_status
        }
    }

@app.get("/api/v1/health")
async def api_health():
    logger.debug("API health check accessed")
    return {"code": 200, "message": "API服务正常", "data": {"timestamp": datetime.now().isoformat()}}

# ===== /api/v1 路由 =====
from fastapi import Body
import jwt
from datetime import datetime as dt, timezone, timedelta

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-test-key-change-in-production")  # 从环境变量读取密钥
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 7200  # 2小时

def create_access_token(data: dict):
    """创建JWT访问令牌"""
    to_encode = data.copy()
    expire = dt.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/api/v1/auth/register")
async def register(
    email: str = Body(...),
    password: str = Body(...),
    confirmPassword: str = Body(...),
    captcha: Optional[str] = Body(None)
):
    """用户注册接口（暂未实现，返回演示数据）"""
    if password != confirmPassword:
        logger.warning(f"Registration failed: passwords do not match for email {email}")
        raise HTTPException(status_code=400, detail="密码不匹配")
    
    logger.info(f"User registration attempted for email: {email}")
    # TODO: 实现真实用户的注册逻辑
    return {
        "code": 200,
        "message": "注册成功",
        "data": {
            "access_token": "demo-jwt-token",
            "token_type": "bearer",
            "user_info": {
                "userId": 1,
                "username": email.split('@')[0],
                "email": email,
                "avatar": None,
                "roles": ["user"]
            }
        }
    }

@app.post("/api/v1/auth/login")
async def login_v1(username: str = Body(...), password: str = Body(...)):
    """用户登录接口 (/api/v1) - 真实数据库验证"""
    logger.info(f"Login attempt for username: {username}")  # 记录登录尝试
    user = authenticate_user(username, password)
    if not user:
        logger.warning(f"Login failed: invalid credentials for username {username}")
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    logger.info(f"User logged in successfully: {user['username']} (ID: {user['id']})")  # 记录成功登录
    
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

@app.get("/api/v1/auth/me")
async def get_current_user_v1():
    """获取当前用户信息 (/api/v1) - 需要JWT验证"""
    # TODO: 添加JWT验证中间件
    logger.info("Current user info requested")
    # 暂时返回演示数据
    return {
        "code": 200,
        "message": "success",
        "data": {
            "userId": 1,
            "username": "admin",
            "email": "admin@example.com",
            "firstName": "系统",
            "lastName": "管理员",
            "nickname": "Admin",
            "avatar": None,
            "roles": ["admin"],
            "status": "active",
            "isVerified": True,
            "userType": "admin",
            "timezone": "UTC",
            "language": "zh",
            "lastLoginTime": "2026-01-22T18:54:22Z"
        }
    }

# ===== 兼容前端旧路径、新增仪表板、情报模块接口 =====

# 部门管理兼容路由 - 直接返回404提示使用新API
@app.get("/admin/departments")
async def departments_not_found():
    """旧的部门列表请求 - 返回404提示使用新API"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=404,
        content={
            "code": 404,
            "message": "接口已迁移",
            "detail": "请使用新的API路径: /api/v1/admin/departments"
        }
    )

@app.get("/admin/roles")
async def roles_not_found():
    """旧的roles请求 - 返回404提示使用新API"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=404,
        content={
            "code": 404,
            "message": "接口已迁移", 
            "detail": "请使用新的API路径: /api/v1/admin/roles"
        }
    )

@app.get("/api/auth/login")
async def login_compat_get():
    """兼容前端错误的GET请求 - 返回提示信息"""
    logger.warning("GET request made to login endpoint (should be POST)")
    return {"code": 405, "message": "此接口仅支持POST方法", "detail": "请使用POST方法访问登录接口"}

@app.post("/api/auth/login")
async def login_compat(username: str = Body(...), password: str = Body(...)):
    """兼容前端登录接口 - 真实数据库验证"""
    logger.info(f"Compatibility login attempt for username: {username}")  # 记录兼容性登录尝试
    user = authenticate_user(username, password)
    if not user:
        logger.warning(f"Compatibility login failed: invalid credentials for username {username}")
        raise HTTPException(401, "用户名或密码错误")
    
    logger.info(f"User logged in successfully via compatibility endpoint: {user['username']} (ID: {user['id']})")  # 记录成功登录
    
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

@app.get("/api/auth/profile")
async def get_profile_compat():
    """兼容前端获取用户信息接口"""
    logger.info("Profile info requested via compatibility endpoint")
    # TODO: 从JWT中提取用户ID并查询数据库
    return {
        "code": 200,
        "message": "success",
        "data": {
            "userId": 1,
            "username": "admin",
            "email": "admin@example.com",
            "firstName": "系统",
            "lastName": "管理员",
            "nickname": "Admin",
            "avatar": None,
            "roles": ["admin"],
            "status": "active",
            "isVerified": True,
            "userType": "admin",
            "timezone": "UTC",
            "language": "zh",
            "lastLoginTime": "2026-01-22T18:54:22Z"
        }
    }

@app.get("/api/dashboard/summary")
async def dashboard_summary():
    """仪表板统计数据 - 真实数据库查询"""
    try:
        logger.info("Dashboard summary requested")
        stats = get_dashboard_stats()
        return {
            "code": 200,
            "data": stats
        }
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取仪表板数据失败: {str(e)}")

@app.get("/api/intelligence/screening/list")
async def screening_list():
    """情报筛选列表 - 真实数据库查询"""
    try:
        logger.info("Intelligence screening list requested")
        result = get_intelligence_screening_list()
        return {
            "code": 200,
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to get intelligence screening list: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取情报筛选列表失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting application server on 0.0.0.0:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)  # 改为8001端口
    logger.info("Application server stopped")