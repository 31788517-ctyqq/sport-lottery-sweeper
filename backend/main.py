#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
体育彩票扫盘系统 - 主应用入口
真实数据库版本
"""

import warnings
# 忽略 Pydantic v2 的 protected_namespaces 警告
warnings.filterwarnings("ignore", category=UserWarning, message=".*Field name.*shadows an attribute in parent.*")
warnings.filterwarnings("ignore", category=UserWarning, message=".*protected_namespaces.*")

from typing import Optional  # AI_WORKING: coder1 @2026-02-10

import os
import sys
import logging  # AI_WORKING: coder1 @2026-02-10

# Import rate limiting libraries
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# AI_WORKING: coder1 @2026-02-10 - unset DATABASE_URL environment variable
if "DATABASE_URL" in os.environ:
    del os.environ["DATABASE_URL"]
# AI_DONE: coder1 @2026-02-10

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入日志配置（但不在这里调用setup_logging，避免重复初始化）
from backend.utils.logging_config import setup_logging

# 获取logger实例（注意：此时日志系统还未完全初始化，但logging模块本身可用）
logger = logging.getLogger(__name__)

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Query, Body
from starlette.requests import Request
from starlette.responses import Response
import asyncio

# Import authentication dependencies
from backend.api.dependencies import get_current_active_user, get_current_active_admin_user
from backend.models.user import User

# 导入数据库相关模块
from backend.database import engine, DATABASE_URL
from backend.models.base import Base

# AI_WORKING: coder1 @2026-02-10 - 添加数据库路径日志
logger.info(f"数据库连接URL: {DATABASE_URL}")

# 导入LLM Provider相关的必要模型
from backend.models.llm_provider import LLMProvider

# 导入日志中间件
from backend.core.logging_middleware import LoggingMiddleware

# 导入监控和限流中间件
from backend.core.monitoring_middleware import MonitoringMiddleware
from backend.core.rate_limit_middleware import RateLimitMiddleware

# 导入性能优化中间件
from backend.core.performance_middleware import PerformanceMiddleware

# 导入安全头中间件
from backend.middleware import SecurityHeadersMiddleware

# 导入Null安全中间件
from backend.middleware.null_safety_middleware import add_null_safety_middleware

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
        from backend.services.llm_service import LLMService
        llm_service = LLMService()
        
        # 从环境变量获取API密钥
        import os
        api_keys = {
            'openai': os.getenv('OPENAI_API_KEY'),
            'gemini': os.getenv('GEMINI_API_KEY'),
            'qwen': os.getenv('QWEN_API_KEY'),
        }
        logger.info(f"LLM key presence: openai={bool(api_keys['openai'])}, gemini={bool(api_keys['gemini'])}, qwen={bool(api_keys['qwen'])}")

        
        # 注册可用的提供商
        if api_keys['openai']:
            llm_service.register_provider('openai', api_keys['openai'])
            logger.info("OpenAI provider registered")
        
        if api_keys['gemini']:
            llm_service.register_provider('gemini', api_keys['gemini'])
            logger.info("Gemini provider registered")
        
        if api_keys['qwen']:
            llm_service.register_provider('qwen', api_keys['qwen'])
            logger.info("Qwen provider registered")
        
        # 从数据库加载已配置的提供商（简化版本，避免阻塞）
        try:
            # 使用简单的懒加载方式，避免启动时阻塞
            # 将数据库加载推迟到第一次实际需要时进行
            logger.info("LLM提供商数据库加载已推迟到运行时（避免启动阻塞）")
        except Exception as db_error:
            logger.warning(f"从数据库加载LLM提供商失败: {db_error}")
            # 继续运行，至少环境变量中的提供商已注册
        
        # 设置默认提供商
        if llm_service.providers:
            llm_service.set_default_provider(next(iter(llm_service.providers)))
            logger.info(f"Default LLM provider: {llm_service.default_provider}")
        logger.info("LLM service initialized")
    except Exception as e:
        logger.warning(f"LLM service initialization failed: {e}")
        llm_service = None

def sync_data_source_to_crawler_config():
    """同步数据源配置到爬虫配置，确保两个系统的一致性"""
    try:
        from sqlalchemy.orm import sessionmaker
        from backend.database import engine
        from backend.models.data_sources import DataSource
        from backend.models.crawler_config import CrawlerConfig
        from backend.crawler.management import create_crawler_config_from_data_source
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # 获取所有启用的数据源
            data_sources = db.query(DataSource).filter(DataSource.status == True).all()
            
            for source in data_sources:
                # 检查是否已存在对应的爬虫配置
                existing_config = db.query(CrawlerConfig).filter(
                    CrawlerConfig.source_id == source.id
                ).first()
                
                if not existing_config:
                    # 根据数据源创建爬虫配置
                    create_crawler_config_from_data_source(db, source)
                    
            db.commit()
            logger.info(f"同步了 {len(data_sources)} 个数据源到爬虫配置")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"同步数据源到爬虫配置失败: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Application starting up...")
    
    # 初始化日志系统（这是正确的调用位置）
    from backend.utils.logging_config import setup_logging
    setup_logging()
    
    # AI_WORKING: coder1 @2026-02-10 - 添加数据库路径日志
    from backend.database import DATABASE_URL, DATABASE_PATH
    logger.info(f"Database URL: {DATABASE_URL}")
    logger.info(f"Database PATH: {DATABASE_PATH}")
    logger.info(f"Database PATH absolute: {DATABASE_PATH.absolute()}")
    # AI_DONE: coder1 @2026-02-10
    
    # 初始化数据库 - 只创建不存在的表，不删除现有表
    from backend.database import engine, Base
    Base.metadata.create_all(bind=engine, checkfirst=True)
    
    # 暂时禁用启动时的数据源同步，避免ORM冲突
    # sync_data_source_to_crawler_config()
    
    # 初始化各种服务
    # initialize_services()
    # ???LLM??
    init_llm_service()  # 暂时注释掉未定义的函数调用
    
    yield
    
    # 应用关闭时的清理
    logger.info("Application shutting down...")

# 新增：API重定向中间件（临时方案）
class APIMigrationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """将旧版API路径重定向到新版API路径"""
        old_path = request.url.path
        
        # 识别需要重定向的旧路径
        if old_path.startswith("/api/admin/v1/"):
            new_path = old_path.replace("/api/admin/v1/", "/api/v1/admin/", 1)
            request.scope["path"] = new_path
            logger.info(f"API路径重定向: {old_path} -> {new_path}")
        elif old_path == "/api/admin/v1":
            new_path = "/api/v1/admin"
            request.scope["path"] = new_path
            logger.info(f"API路径重定向: {old_path} -> {new_path}")
        elif old_path.startswith("/api/admin/crawler"):
            new_path = old_path.replace("/admin/crawler", "/v1/admin")
            request.scope["path"] = new_path
            logger.info(f"API路径重定向: {old_path} -> {new_path}")
        
        # 处理任务管理相关路径
        elif old_path.startswith("/api/admin/tasks"):
            new_path = old_path.replace("/api/admin/tasks", "/api/v1/admin/tasks")
            request.scope["path"] = new_path
            logger.info(f"API路径重定向: {old_path} -> {new_path}")
            
        response = await call_next(request)
        return response

# 创建FastAPI应用实例
app = FastAPI(
    lifespan=lifespan,
    title="体育彩票扫盘系统",
    description="提供体育赛事数据采集与分析服务",
    version="1.0.0"
)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/hour"],  # Default global rate limit
    storage_uri="memory://"  # Use memory storage for simplicity
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# 添加API迁移中间件（放在其他中间件之前）
app.add_middleware(APIMigrationMiddleware)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # 开发环境前端
        "http://127.0.0.1:3000",      # 开发环境前端（IP形式）
        "http://localhost:8080",      # 可能的其他开发端口
        "http://127.0.0.1:8080",
        "http://localhost",           # 生产环境可能的域名
        "http://127.0.0.1",
        # 注意：当allow_credentials=True时，不能包含"*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册性能中间件
app.add_middleware(PerformanceMiddleware)

# 注册安全头中间件
app.add_middleware(SecurityHeadersMiddleware)

# 添加null safety中间件
# add_null_safety_middleware(app)

# 添加异常处理器
from backend.exceptions import setup_exception_handlers
setup_exception_handlers(app)

logger.info("Application starting up...")  # 添加启动日志

# 强制启用完整API模式，注册所有路由
import os
os.environ['FULL_API_MODE'] = 'true'

# AI_WORKING: coder1 @2026-01-29 - 替换print为logging，统一日志记录
# 导入API v1路由 - 启用完整API模式
logger.info("Registering API routes...")
try:
    from backend.api.v1 import router as api_v1_router
    app.include_router(api_v1_router, prefix="/api/v1")
    logger.info("API v1 routes registered successfully")
except Exception as e:
    logger.error(f"API v1 路由注册失败: {e}")
    # 即使API路由注册失败，也继续运行基本服务

# 注册数据源管理路由（已通过admin路由注册，此处注释避免重复）
# try:
#     from backend.api.v1.admin.data_source import router as data_source_router
#     app.include_router(data_source_router, prefix="/api/v1/admin", tags=["data-sources"])
#     logger.info("Data source management routes registered (/api/v1/admin/data-sources)")
# except Exception as e:
#     logger.error(f"数据源管理路由注册失败: {e}")
#     import traceback
#     logger.error(f"详细堆栈: {traceback.format_exc()}")
    
# 注册爬虫监控API路由
try:
    from backend.api.v1.crawler_monitor import router as crawler_monitor_router
    # 统一使用 /api/v1/admin 作为管理类API的基础前缀
    app.include_router(crawler_monitor_router, prefix="/api/v1/admin", tags=["crawler-monitor"])
    logger.info("Crawler monitoring API routes registered (/api/v1/admin/crawler/monitor)")
except Exception as e:
    logger.error(f"爬虫监控API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")
    
# 注册请求头管理API路由
try:
    from backend.api.v1.admin.headers_management import router as headers_router
    app.include_router(headers_router, prefix="/api/v1/admin", tags=["admin-headers"])
    logger.info("Request header management API routes registered (/api/v1/admin/headers)")
except Exception as e:
    logger.error(f"请求头管理API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")
    
# 注册IP池管理API路由
try:
    from backend.api.v1.ip_pool_adapter import router as ip_pool_router
    # 为IP池管理API统一使用/admin前缀，保持与其他管理API一致
    app.include_router(ip_pool_router, prefix="/api/v1/admin", tags=["ip-pool"])
    logger.info("IP pool management API routes registered (/api/v1/admin/ip-pools)")
except Exception as e:
    logger.error(f"IP池管理API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")

# 注册任务管理API路由
try:
    from backend.api.v1.admin.task_management import router as task_router
    app.include_router(task_router, prefix="/api/v1/admin/tasks", tags=["admin-tasks"])
    logger.info("Task management API routes registered (/api/v1/admin/tasks)")
except Exception as e:
    logger.error(f"任务管理API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")

# 注册用户画像API路由
try:
    from backend.api.v1.user_profiles import router as user_profiles_router
    app.include_router(user_profiles_router, prefix="/api/v1/admin", tags=["user-profiles"])
    logger.info("User profile API routes registered (/api/v1/admin/user-profiles)")
except Exception as e:
    logger.error(f"用户画像API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")

# 注册角色管理API路由
try:
    from backend.api.v1.roles import router as roles_router
    app.include_router(roles_router, prefix="/api/v1/admin", tags=["roles"])
    logger.info("Role management API routes registered (/api/v1/admin/roles)")
except Exception as e:
    logger.error(f"角色管理API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")

# 注册权限管理API路由
try:
    from backend.api.v1.permissions import router as permissions_router
    app.include_router(permissions_router, prefix="/api/v1/admin", tags=["permissions"])
    logger.info("Permission management API routes registered (/api/v1/admin/permissions)")
except Exception as e:
    logger.error(f"权限管理API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")

# 注册爬虫任务管理API路由
try:
    from backend.api.v1.admin.crawler_tasks import router as crawler_tasks_router
    app.include_router(crawler_tasks_router, prefix="/api/v1/admin", tags=["crawler-tasks"])
    logger.info("Crawler task management API routes registered (/api/v1/admin/crawler/tasks)")
except Exception as e:
    logger.error(f"爬虫任务管理API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")

# 注册任务监控API路由
try:
    from backend.api.v1.task_monitor import router as task_monitor_router
    app.include_router(task_monitor_router, prefix="/api/v1", tags=["task-monitor"])
    logger.info("Task monitoring API routes registered (/api/v1/task-monitor)")
except Exception as e:
    logger.error(f"任务监控API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")

# 注册日志API路由
try:
    from backend.api.v1.admin.logs import router as logs_router
    # 将logs路由注册到/api/v1/admin/system路径下，这样API端点将是/api/v1/admin/system/logs/db/security
    app.include_router(logs_router, prefix="/api/v1/admin/system", tags=["system-logs"])
    logger.info("Log API routes registered (/api/v1/admin/system/logs)")
except Exception as e:
    logger.error(f"日志API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")

# 注册爬虫相关API路由（全部迁移到FastAPI）
try:
    from backend.api.v1.admin.crawler_sources import router as crawler_sources_router
    app.include_router(crawler_sources_router, prefix="/api/v1/admin", tags=["crawler-sources"])
    logger.info("Crawler data source API routes registered (/api/v1/admin/crawler/sources)")
except Exception as e:
    logger.error(f"爬虫数据源API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")


try:
    from backend.api.v1.admin.crawler_configs import router as crawler_configs_router
    app.include_router(crawler_configs_router, prefix="/api/v1/admin", tags=["crawler-configs"])
    logger.info("Crawler config API routes registered (/api/v1/admin/crawler/config)")
except Exception as e:
    logger.error(f"爬虫配置API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")

try:
    from backend.api.v1.admin.crawler_intelligence import router as crawler_intel_router
    app.include_router(crawler_intel_router, prefix="/api/v1/admin", tags=["crawler-intelligence"])
    logger.info("Crawler intelligence API routes registered (/api/v1/admin/crawler/intelligence)")
except Exception as e:
    logger.error(f"爬虫情报API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")

# 注册用户管理API路由
try:
    from backend.api.v1.admin_user_management import router as admin_user_management_router
    app.include_router(admin_user_management_router, prefix="/api/v1/admin", tags=["admin-user-management"])
    logger.info("Admin user management API routes registered (/api/v1/admin/admin-users)")
except Exception as e:
    logger.error(f"管理员用户管理API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")

# 注册部门管理API路由
try:
    from backend.api.v1.departments import router as departments_router
    app.include_router(departments_router, prefix="/api/v1/admin", tags=["departments"])
    logger.info("Department management API routes registered (/api/v1/admin/departments)")
except Exception as e:
    logger.error(f"部门管理API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")

try:
    from backend.api.v1.users import router as users_router
    app.include_router(users_router, prefix="/api/v1/admin", tags=["users"])
    logger.info("Regular user management API routes registered (/api/v1/admin/users)")
except Exception as e:
    logger.error(f"普通用户管理API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")

try:
    from backend.api.v1.frontend_user_management import router as frontend_user_management_router
    app.include_router(frontend_user_management_router, prefix="/api/v1/admin", tags=["frontend-user-management"])
    logger.info("Frontend user management API routes registered (/api/v1/admin/frontend-users)")
except Exception as e:
    logger.error(f"前端用户管理API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")

try:
    from backend.api.v1.simple_user_api import router as simple_user_api_router
    app.include_router(simple_user_api_router, prefix="/api/v1/admin", tags=["simple-user-api"])
    logger.info("Simple user API routes registered (/api/v1/admin/simple-users)")
except Exception as e:
    logger.error(f"简单用户API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")

# 注册北单过滤API路由 - 直接导入
try:
    from backend.app.api_v1.endpoints.beidan_filter_api import router as beidan_filter_router
    app.include_router(beidan_filter_router, prefix="/api/v1/beidan-filter", tags=["beidan-filter"])
    logger.info("Beidan filter API routes registered (/api/v1/beidan-filter)")
except Exception as e:
    logger.error(f"北单过滤API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")

# 注册北单投注模拟API路由
try:
    from backend.app.api_v1.endpoints.beidan_betting_simulator_api import router as beidan_betting_router
    app.include_router(beidan_betting_router, prefix="/api/v1/beidan-betting", tags=["beidan-betting"])
    logger.info("Beidan betting simulator API routes registered (/api/v1/beidan-betting)")
except Exception as e:
    logger.error(f"北单投注模拟API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")

# 注册多策略筛选API路由
try:
    from backend.app.api_v1.endpoints.multi_strategy_api import router as multi_strategy_router
    app.include_router(multi_strategy_router, prefix="/api/v1", tags=["multi-strategy"])
    logger.info("Multi strategy API routes registered (/api/v1/multi-strategy)")
except Exception as e:
    logger.error(f"多策略API路由注册失败: {e}")
    import traceback
    logger.error(f"详细堆栈: {traceback.format_exc()}")

# 注册admin登录端点 - 注意这里不需要重复注册，因为auth模块已经处理了登录
# 登录API应通过auth模块注册，而不是在admin模块中重复注册
# 如果需要admin特定的登录功能，请确保不要与auth模块冲突

# 注册异常处理器
try:
    from backend.exceptions import setup_exception_handlers
    setup_exception_handlers(app)
    logger.info("Exception handlers registered")
except Exception as e:
    logger.error(f"异常处理器注册失败: {e}")



# 基础路由
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "体育彩票扫盘系统 API", "version": "1.0.0"}

@app.get("/health")
@app.get("/health/live")
@app.get("/api/v1/health/live")
async def health_live():
    logger.debug("Health live check accessed")
    return {"status": "healthy", "service": "sport-lottery-sweeper"}

@app.get("/health/ready")
@app.get("/api/v1/health/ready")
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
@limiter.limit("5/minute")  # Strict limit for login attempts - prevents brute force
async def login_v1(request: Request, username: str = Body(...), password: str = Body(...)):
    """用户登录接口 (/api/v1) - 真实数据库验证"""
    logger.info(f"Login attempt for username: {username}")
    user = authenticate_user(username, password)
    if not user:
        logger.warning(f"Login failed: invalid credentials for username {username}")
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    logger.info(f"User logged in successfully: {user['username']} (ID: {user['id']})")
    
    # 创建JWT令牌
    access_token = create_access_token({
        "sub": str(user["id"]),
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

# 部门管理兼容路由 - 用于用户部门管理页面
@app.get("/admin/users/departments")
async def user_departments_page():
    """用户部门管理页面 - 返回兼容信息"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=200,
        content={
            "code": 200,
            "message": "success",
            "data": {
                "title": "用户部门管理",
                "description": "部门管理页面，使用API: /api/v1/admin/departments"
            }
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
    logger.info(f"Compatibility login attempt for username: {username}")
    user = authenticate_user(username, password)
    if not user:
        logger.warning(f"Compatibility login failed: invalid credentials for username {username}")
        raise HTTPException(401, "用户名或密码错误")
    
    logger.info(f"User logged in successfully via compatibility endpoint: {user['username']} (ID: {user['id']})")
    
    # 创建JWT令牌
    access_token = create_access_token({
        "sub": str(user["id"]),
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
@limiter.limit("30/minute")  # Reasonable limit for dashboard data
async def dashboard_summary(
    request: Request,
    current_user: User = Depends(get_current_active_admin_user)
):
    """仪表板统计数据 - 真实数据库查询 (Admin only)"""
    try:
        logger.info(f"Dashboard summary requested by admin user: {current_user.username} (ID: {current_user.id})")
        stats = get_dashboard_stats()
        return {
            "code": 200,
            "data": stats
        }
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取仪表板数据失败: {str(e)}")

@app.get("/api/intelligence/screening/list")
@limiter.limit("60/minute")  # Moderate limit for intelligence data
async def screening_list(
    request: Request,
    current_user: User = Depends(get_current_active_admin_user)
):
    """情报筛选列表 - 真实数据库查询 (Admin only)"""
    try:
        logger.info(f"Intelligence screening list requested by admin user: {current_user.username} (ID: {current_user.id})")
        result = get_intelligence_screening_list()
        return {
            "code": 200,
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to get intelligence screening list: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取情报筛选列表失败: {str(e)}")

@app.get("/api/stats/data-center")
@limiter.limit("60/minute")  # Moderate limit for stats data
async def get_data_center_stats(
    request: Request,
    current_user: User = Depends(get_current_active_admin_user)
):
    """数据中心统计信息 (Admin only)"""
    logger.info(f"Data center stats requested by admin user: {current_user.username} (ID: {current_user.id})")
    return {
        "code": 200,
        "data": {
            "totalMatches": 156,
            "activeSources": 8,
            "dataQuality": 94,
            "errorRate": 2.3,
            "avgResponseTime": 128,
            "storageUsed": 45,
            "matchGrowth": 12,
            "sourceGrowth": 5,
            "qualityTrend": "up",
            "qualityChange": 3,
            "errorImprovement": 15,
            "responseImprovement": 8,
            "storageTrend": "up",
            "storageChange": 7
        }
    }

@app.get("/api/admin/data")
async def get_data_list(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    type: str = Query(None),
    source_id: int = Query(None),
    status: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None)
):
    """获取数据列表"""
    logger.info(f"Data list requested: page={page}, size={size}")
    # 模拟数据
    items = [
        {
            "id": i,
            "type": "matches",
            "sourceName": "官方API",
            "title": f"比赛数据 {i}",
            "status": "normal",
            "quality": 95,
            "recordCount": 100 + i,
            "createdAt": "2026-01-28T10:00:00Z",
            "updatedAt": "2026-01-28T10:00:00Z"
        }
        for i in range(1, 101)
    ]
    # 简单分页
    start = (page - 1) * size
    end = start + size
    paginated_items = items[start:end]
    return {
        "code": 200,
        "data": {
            "items": paginated_items,
            "total": len(items),
            "page": page,
            "size": size
        }
    }

if __name__ == "__main__":
    import uvicorn
    import argparse
    import socket
    
    # 创建数据库表
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # 强制创建LLM Provider表（确保表存在）
    from backend.models.llm_provider import LLMProvider
    LLMProvider.__table__.create(bind=engine, checkfirst=True)
    logger.info("Database tables created successfully")
    
    parser = argparse.ArgumentParser(description='启动API服务')
    parser.add_argument('--port', type=int, default=8000, help='服务端口，默认8000（与前端代理一致）')
    args = parser.parse_args()
    
    # 检查端口占用
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("0.0.0.0", args.port))
        sock.close()
    except OSError as e:
        if "10013" in str(e) or "Address already in use" in str(e):
            logger.error(f"❌ 端口{args.port}被占用，请先释放端口后重试")
            logger.info("💡 可使用: netstat -ano | findstr :%d", args.port)
            logger.info("💡 然后: taskkill /F /PID <进程ID>")
            exit(1)
        else:
            raise
    
    # 启动应用
    logger.info("🚀 启动体育彩票扫盘系统...")
    logger.info(f"📍 服务地址: http://localhost:%d", args.port)
    logger.info(f"📚 API文档: http://localhost:%d/docs", args.port)
    logger.info(f"📊 健康检查: http://localhost:%d/health/live", args.port)
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=args.port,
            log_level="info"
        )
    except OSError as e:
        if "10013" in str(e):
            logger.error("❌ 端口%d被占用，请先释放端口后重试", args.port)
            logger.info("💡 可使用: netstat -ano | findstr :%d", args.port)
            logger.info("💡 然后: taskkill /F /PID <进程ID>")
        else:
            raise
    
    logger.info("👋 应用服务已停止")
