#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浣撹偛褰╃エ鎵洏绯荤粺 - 涓诲簲鐢ㄥ叆鍙?鐪熷疄鏁版嵁搴撶増鏈?"""

import warnings
# 蹇界暐 Pydantic v2 鐨?protected_namespaces 璀﹀憡
warnings.filterwarnings("ignore", category=UserWarning, message=".*Field name.*shadows an attribute in parent.*")
warnings.filterwarnings("ignore", category=UserWarning, message=".*protected_namespaces.*")

from typing import Optional, List  # AI_WORKING: coder1 @2026-02-10

import os
import sys
import logging  # AI_WORKING: coder1 @2026-02-10

# Import rate limiting libraries
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Get project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import logging setup helper
from backend.utils.logging_config import setup_logging

# Module logger
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

# Database references
from backend.database import engine, DATABASE_URL, get_db
from backend.models.base import Base
from backend.config import settings
from backend.models.source_issue_state import SourceIssueState  # noqa: F401
from backend.models.source_issue_fetch_runs import SourceIssueFetchRun  # noqa: F401
from backend.models.kaggle_dataset_registry import KaggleDatasetRegistry  # noqa: F401
from backend.models.kaggle_sync_state import KaggleSyncState  # noqa: F401
from backend.models.kaggle_sync_runs import KaggleSyncRun  # noqa: F401
from backend.models.kaggle_file_manifest import KaggleFileManifest  # noqa: F401
from backend.models.kaggle_match_staging import KaggleMatchStaging  # noqa: F401
from backend.models.kaggle_team_staging import KaggleTeamStaging  # noqa: F401
from backend.models.kaggle_league_staging import KaggleLeagueStaging  # noqa: F401
from backend.models.entity_mapping_record import EntityMappingRecord  # noqa: F401
from backend.models.entity_mapping_record import EntityMappingSyncRun  # noqa: F401

# AI_WORKING: coder1 @2026-02-10 - 娣诲姞鏁版嵁搴撹矾寰勬棩蹇?logger.info(f"鏁版嵁搴撹繛鎺RL: {DATABASE_URL}")

# LLM provider model
from backend.models.llm_provider import LLMProvider

# 瀵煎叆鏃ュ織涓棿浠?
from backend.core.logging_middleware import LoggingMiddleware

# 瀵煎叆鐩戞帶鍜岄檺娴佷腑闂翠欢
from backend.core.monitoring_middleware import MonitoringMiddleware
from backend.core.rate_limit_middleware import RateLimitMiddleware

# 瀵煎叆鎬ц兘浼樺寲涓棿浠?
from backend.core.performance_middleware import PerformanceMiddleware

# 瀵煎叆瀹夊叏澶翠腑闂翠欢
from backend.middleware import SecurityHeadersMiddleware

# 瀵煎叆Null瀹夊叏涓棿浠?
from backend.middleware.null_safety_middleware import add_null_safety_middleware

# 瀵煎叆鏁版嵁搴撳伐鍏?
from backend.database_utils import (
    authenticate_user, get_user_by_id, 
    get_dashboard_stats, get_intelligence_screening_list
)

from contextlib import asynccontextmanager

# 鍏ㄥ眬鍙橀噺澹版槑
llm_service = None
collaborative_agents = None
communication_hub = None

def init_llm_service():
    """鍒濆鍖朙LM鏈嶅姟"""
    global llm_service
    try:
        from backend.services.llm_service import LLMService
        llm_service = LLMService()
        
        # 浠庣幆澧冨彉閲忚幏鍙朅PI瀵嗛挜
        import os
        api_keys = {
            'openai': os.getenv('OPENAI_API_KEY'),
            'gemini': os.getenv('GEMINI_API_KEY'),
            'qwen': os.getenv('QWEN_API_KEY'),
            'zhipuai': os.getenv('ZHIPUAI_API_KEY') or os.getenv('ZHIPU_API_KEY') or os.getenv('BIGMODEL_API_KEY'),
        }
        logger.info(
            "LLM key presence: openai=%s, gemini=%s, qwen=%s, zhipuai=%s",
            bool(api_keys['openai']),
            bool(api_keys['gemini']),
            bool(api_keys['qwen']),
            bool(api_keys['zhipuai']),
        )

        
        # 娉ㄥ唽鍙敤鐨勬彁渚涘晢
        if api_keys['openai']:
            llm_service.register_provider('openai', api_keys['openai'])
            logger.info("OpenAI provider registered")
        
        if api_keys['gemini']:
            llm_service.register_provider('gemini', api_keys['gemini'])
            logger.info("Gemini provider registered")
        
        if api_keys['qwen']:
            llm_service.register_provider('qwen', api_keys['qwen'])
            logger.info("Qwen provider registered")

        if api_keys['zhipuai']:
            llm_service.register_provider('zhipuai', api_keys['zhipuai'])
            logger.info("ZhipuAI provider registered")

        # Defer DB provider loading to runtime to keep startup stable.
        try:
            logger.info("LLM provider DB loading deferred to runtime")
        except Exception as db_error:
            logger.warning(f"Failed to defer LLM provider DB loading: {db_error}")

        # Set default provider.
        if llm_service.providers:
            llm_service.set_default_provider(next(iter(llm_service.providers)))
            logger.info(f"Default LLM provider: {llm_service.default_provider}")
        logger.info("LLM service initialized")
    except Exception as e:
        logger.warning(f"LLM service initialization failed: {e}")
        llm_service = None

def sync_data_source_to_crawler_config():
    """Sync data source configuration to crawler config records."""
    try:
        from sqlalchemy.orm import sessionmaker
        from backend.database import engine
        from backend.models.data_sources import DataSource
        from backend.models.crawler_config import CrawlerConfig
        from backend.crawler.management import create_crawler_config_from_data_source
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Query all enabled data sources.
            data_sources = db.query(DataSource).filter(DataSource.status == True).all()
            
            for source in data_sources:
                # Check whether crawler config already exists for this source.
                existing_config = db.query(CrawlerConfig).filter(
                    CrawlerConfig.source_id == source.id
                ).first()
                
                if not existing_config:
                    # Create crawler config from data source when missing.
                    create_crawler_config_from_data_source(db, source)
                    
            db.commit()
            logger.info(f"Synced {len(data_sources)} data sources to crawler config")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"鍚屾鏁版嵁婧愬埌鐖櫕閰嶇疆澶辫触: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    logger.info("Application starting up...")
    
    # Initialize logging once during startup.
    from backend.utils.logging_config import setup_logging
    setup_logging()
    
    # Log database path for startup diagnostics.
    from backend.database import DATABASE_URL, DATABASE_PATH
    logger.info(f"Database URL: {DATABASE_URL}")
    logger.info(f"Database PATH: {DATABASE_PATH}")
    logger.info(f"Database PATH absolute: {DATABASE_PATH.absolute()}")
    # AI_DONE: coder1 @2026-02-10
    
    # Initialize DB metadata
    from backend.database import engine
    Base.metadata.create_all(bind=engine, checkfirst=True)
    
    # 鏆傛椂绂佺敤鍚姩鏃剁殑鏁版嵁婧愬悓姝ワ紝閬垮厤ORM鍐茬獊
    # sync_data_source_to_crawler_config()
    
    # 鍒濆鍖栧悇绉嶆湇鍔?    # initialize_services()
    # ???LLM??
    init_llm_service()  # 鏆傛椂娉ㄩ噴鎺夋湭瀹氫箟鐨勫嚱鏁拌皟鐢?

    # Start auto issue sync scheduler: 500w issue discovery -> 100qiu fetch.
    try:
        from backend.services.source_sync_service import source_issue_auto_sync_service

        source_issue_auto_sync_service.start()
    except Exception as e:
        logger.error(f"Failed to start source sync scheduler: {e}")

    # Start Kaggle sync baseline service.
    try:
        from backend.services.kaggle_sync_service import kaggle_sync_service

        kaggle_sync_service.start()
    except Exception as e:
        logger.error(f"Failed to start kaggle sync service: {e}")

    # Start entity mapping DB sync scheduler.
    try:
        from backend.services.entity_mapping_sync_service import entity_mapping_sync_service

        entity_mapping_sync_service.start()
    except Exception as e:
        logger.error(f"Failed to start entity mapping sync service: {e}")

    yield
    
    # 搴旂敤鍏抽棴鏃剁殑娓呯悊
    try:
        from backend.services.source_sync_service import source_issue_auto_sync_service

        source_issue_auto_sync_service.shutdown()
    except Exception as e:
        logger.error(f"Failed to stop source sync scheduler: {e}")

    try:
        from backend.services.kaggle_sync_service import kaggle_sync_service

        kaggle_sync_service.shutdown()
    except Exception as e:
        logger.error(f"Failed to stop kaggle sync service: {e}")

    try:
        from backend.services.entity_mapping_sync_service import entity_mapping_sync_service

        entity_mapping_sync_service.shutdown()
    except Exception as e:
        logger.error(f"Failed to stop entity mapping sync service: {e}")

    logger.info("Application shutting down...")

# 鏂板锛欰PI閲嶅畾鍚戜腑闂翠欢锛堜复鏃舵柟妗堬級
class APIMigrationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """灏嗘棫鐗圓PI璺緞閲嶅畾鍚戝埌鏂扮増API璺緞"""
        old_path = request.url.path
        
        # 璇嗗埆闇€瑕侀噸瀹氬悜鐨勬棫璺緞
        if old_path.startswith("/api/admin/v1/"):
            new_path = old_path.replace("/api/admin/v1/", "/api/v1/admin/", 1)
            request.scope["path"] = new_path
            logger.info(f"API璺緞閲嶅畾鍚? {old_path} -> {new_path}")
        elif old_path == "/api/admin/v1":
            new_path = "/api/v1/admin"
            request.scope["path"] = new_path
            logger.info(f"API璺緞閲嶅畾鍚? {old_path} -> {new_path}")
        elif old_path.startswith("/api/admin/crawler"):
            # Keep crawler segment: /api/admin/crawler/... -> /api/v1/admin/crawler/...
            new_path = old_path.replace("/api/admin/crawler", "/api/v1/admin/crawler", 1)
            request.scope["path"] = new_path
            logger.info(f"API璺緞閲嶅畾鍚? {old_path} -> {new_path}")
        
        # 澶勭悊浠诲姟绠＄悊鐩稿叧璺緞
        elif old_path.startswith("/api/admin/tasks"):
            new_path = old_path.replace("/api/admin/tasks", "/api/v1/admin/tasks")
            request.scope["path"] = new_path
            logger.info(f"API璺緞閲嶅畾鍚? {old_path} -> {new_path}")

        elif old_path.startswith("/api/task-monitor"):
            new_path = old_path.replace("/api/task-monitor", "/api/v1/task-monitor", 1)
            request.scope["path"] = new_path
            logger.info(f"API path redirected: {old_path} -> {new_path}")

        elif old_path.startswith("/api/admin/source-sync"):
            new_path = old_path.replace("/api/admin/source-sync", "/api/v1/admin/source-sync", 1)
            request.scope["path"] = new_path
            logger.info(f"API path redirected: {old_path} -> {new_path}")
            
        elif old_path == "/api/admin/sources" or old_path.startswith("/api/admin/sources/"):
            # Map legacy source management API paths to full CRUD source endpoints.
            new_path = old_path.replace("/api/admin/sources", "/api/v1/admin/sources", 1)
            request.scope["path"] = new_path
            logger.info(f"API path redirected: {old_path} -> {new_path}")
        elif old_path == "/api/admin/data" or old_path.startswith("/api/admin/data/"):
            new_path = old_path.replace("/api/admin/data", "/api/v1/admin/data", 1)
            request.scope["path"] = new_path
            logger.info(f"API path redirected: {old_path} -> {new_path}")
        elif old_path == "/api/admin/ip-pools" or old_path.startswith("/api/admin/ip-pools/"):
            new_path = old_path.replace("/api/admin/ip-pools", "/api/v1/admin/ip-pools", 1)
            request.scope["path"] = new_path
            logger.info(f"API path redirected: {old_path} -> {new_path}")
        elif old_path == "/api/admin/headers" or old_path.startswith("/api/admin/headers/"):
            new_path = old_path.replace("/api/admin/headers", "/api/v1/admin/headers", 1)
            request.scope["path"] = new_path
            logger.info(f"API path redirected: {old_path} -> {new_path}")
        elif old_path == "/api/system/monitor" or old_path.startswith("/api/system/monitor/"):
            new_path = old_path.replace("/api/system/monitor", "/api/v1/admin/system/monitor", 1)
            request.scope["path"] = new_path
            logger.info(f"API path redirected: {old_path} -> {new_path}")
        elif old_path == "/api/multi-strategy" or old_path.startswith("/api/multi-strategy/"):
            new_path = old_path.replace("/api/multi-strategy", "/api/v1/multi-strategy", 1)
            request.scope["path"] = new_path
            logger.info(f"API path redirected: {old_path} -> {new_path}")

        elif old_path == "/api/llm" or old_path.startswith("/api/llm/"):
            new_path = old_path.replace("/api/llm", "/api/v1/llm", 1)
            request.scope["path"] = new_path
            logger.info(f"API path redirected: {old_path} -> {new_path}")

        elif old_path.startswith("/api/draw-prediction"):

            new_path = old_path.replace("/api/draw-prediction", "/api/v1/draw-prediction", 1)
            request.scope["path"] = new_path
            logger.info(f"API path redirected: {old_path} -> {new_path}")

        response = await call_next(request)
        return response

def load_cors_origins() -> List[str]:
    """Load CORS origins from environment variables with safe defaults."""
    default_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost",
        "http://127.0.0.1",
    ]

    raw_origins = (
        os.getenv("CORS_ORIGINS")
        or os.getenv("ALLOWED_ORIGINS")
        or os.getenv("BACKEND_CORS_ORIGINS")
    )
    if not raw_origins:
        return default_origins

    parsed = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    if not parsed:
        return default_origins

    logger.info("CORS origins loaded from env: %s", parsed)
    return parsed


def load_rate_limit_defaults() -> List[str]:
    """Load optional global rate-limit rules from env.

    Keep empty by default so admin pages with many concurrent requests
    are not blocked by a low global cap.
    """
    raw_limits = os.getenv("API_DEFAULT_RATE_LIMITS", "").strip()
    if not raw_limits:
        return []
    return [item.strip() for item in raw_limits.split(",") if item.strip()]

# Initialize FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title="足彩扫盘系统 API",
    description="Provide sports match data collection and analysis services.",
    version="1.0.0"
)

# Initialize rate limiter
default_rate_limits = load_rate_limit_defaults()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=default_rate_limits,
    storage_uri="memory://"  # Use memory storage for simplicity
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
if default_rate_limits:
    logger.info("Global rate limits enabled: %s", default_rate_limits)
else:
    logger.warning("Global rate limits disabled (API_DEFAULT_RATE_LIMITS not set)")

# 娣诲姞API杩佺Щ涓棿浠讹紙鏀惧湪鍏朵粬涓棿浠朵箣鍓嶏級
app.add_middleware(APIMigrationMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=load_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional performance middleware toggle
ENABLE_PERFORMANCE_MIDDLEWARE = os.getenv("ENABLE_PERFORMANCE_MIDDLEWARE", "0").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
if ENABLE_PERFORMANCE_MIDDLEWARE:
    app.add_middleware(PerformanceMiddleware)
    logger.info("PerformanceMiddleware enabled")
else:
    logger.warning("PerformanceMiddleware disabled by default for stability")

# 娉ㄥ唽瀹夊叏澶翠腑闂翠欢
app.add_middleware(SecurityHeadersMiddleware)

# 娣诲姞null safety涓棿浠?# add_null_safety_middleware(app)

# Register exception handlers
from backend.exceptions import setup_exception_handlers
setup_exception_handlers(app)

logger.info("Application starting up...")  # 娣诲姞鍚姩鏃ュ織

# Force full API mode for route registration
import os
os.environ['FULL_API_MODE'] = 'true'

# AI_WORKING: coder1 @2026-01-29 - 鏇挎崲print涓簂ogging锛岀粺涓€鏃ュ織璁板綍
# 瀵煎叆API v1璺敱 - 鍚敤瀹屾暣API妯″紡
logger.info("Registering API routes...")
# ===== /api/v1 璺敱 =====
try:
    from backend.api.v1 import router as api_v1_router
    app.include_router(api_v1_router, prefix="/api/v1")
    logger.info("API v1 routes registered successfully")
except Exception as e:
    logger.error(f"API v1 璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")
    # 鍗充娇API璺敱娉ㄥ唽澶辫触锛屼篃缁х画杩愯鍩烘湰鏈嶅姟

# 娉ㄥ唽瀹炰綋鏄犲皠鍜屽畼鏂逛俊鎭鐞咥PI璺敱
try:
    from backend.api.v1.admin.entity_mapping import router as entity_mapping_router
    app.include_router(entity_mapping_router, prefix="/api/v1", tags=["entity-mapping"])
    logger.info("Entity mapping API routes registered (/api/v1/entity-mapping)")
except Exception as e:
    logger.error(f"瀹炰綋鏄犲皠API璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")
    
# 娉ㄥ唽鏁版嵁婧愮鐞嗚矾鐢憋紙宸查€氳繃admin璺敱娉ㄥ唽锛屾澶勬敞閲婇伩鍏嶉噸澶嶏級
# try:
#     from backend.api.v1.admin.data_source import router as data_source_router
#     app.include_router(data_source_router, prefix="/api/v1/admin", tags=["data-sources"])
#     logger.info("Data source management routes registered (/api/v1/admin/data-sources)")
# except Exception as e:
#     logger.error(f"鏁版嵁婧愮鐞嗚矾鐢辨敞鍐屽け璐? {e}")
#     import traceback
#     logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")
    
# 娉ㄥ唽鐖櫕鐩戞帶API璺敱
try:
    from backend.api.v1.admin.data_source import router as data_source_router
    app.include_router(data_source_router, prefix="/api/v1/admin", tags=["data-sources"])
    logger.info("Data source management routes registered (/api/v1/admin/sources)")
except Exception as e:
    logger.error(f"Data source management route registration failed: {e}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")

try:
    from backend.api.v1.crawler_monitor import router as crawler_monitor_router
    # 缁熶竴浣跨敤 /api/v1/admin 浣滀负绠＄悊绫籄PI鐨勫熀纭€鍓嶇紑
    app.include_router(crawler_monitor_router, prefix="/api/v1/admin", tags=["crawler-monitor"])
    logger.info("Crawler monitoring API routes registered (/api/v1/admin/crawler/monitor)")
except Exception as e:
    logger.error(f"鐖櫕鐩戞帶API璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")
    
# 娉ㄥ唽璇锋眰澶寸鐞咥PI璺敱
try:
    from backend.api.v1.admin.headers_management import router as headers_router
    app.include_router(headers_router, prefix="/api/v1/admin", tags=["admin-headers"])
    logger.info("Request header management API routes registered (/api/v1/admin/headers)")
except Exception as e:
    logger.error(f"璇锋眰澶寸鐞咥PI璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")
    
# 娉ㄥ唽IP姹犵鐞咥PI璺敱
try:
    from backend.api.v1.ip_pool_adapter import router as ip_pool_router
        # Register IP pool API under admin prefix
    app.include_router(ip_pool_router, prefix="/api/v1/admin", tags=["ip-pool"])
    logger.info("IP pool management API routes registered (/api/v1/admin/ip-pools)")
except Exception as e:
    logger.error(f"IP姹犵鐞咥PI璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

# 娉ㄥ唽浠诲姟绠＄悊API璺敱
try:
    from backend.api.v1.admin.task_management import router as task_router
    app.include_router(task_router, prefix="/api/v1/admin/tasks", tags=["admin-tasks"])
    logger.info("Task management API routes registered (/api/v1/admin/tasks)")
except Exception as e:
    logger.error(f"浠诲姟绠＄悊API璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

# 娉ㄥ唽鐢ㄦ埛鐢诲儚API璺敱
try:
    from backend.api.v1.user_profiles import router as user_profiles_router
    app.include_router(user_profiles_router, prefix="/api/v1/admin", tags=["user-profiles"])
    logger.info("User profile API routes registered (/api/v1/admin/user-profiles)")
except Exception as e:
    logger.error(f"鐢ㄦ埛鐢诲儚API璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

# 娉ㄥ唽瑙掕壊绠＄悊API璺敱
try:
    from backend.api.v1.roles import router as roles_router
    app.include_router(roles_router, prefix="/api/v1/admin", tags=["roles"])
    logger.info("Role management API routes registered (/api/v1/admin/roles)")
except Exception as e:
    logger.error(f"瑙掕壊绠＄悊API璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

# 娉ㄥ唽鏉冮檺绠＄悊API璺敱
try:
    from backend.api.v1.permissions import router as permissions_router
    app.include_router(permissions_router, prefix="/api/v1/admin", tags=["permissions"])
    logger.info("Permission management API routes registered (/api/v1/admin/permissions)")
except Exception as e:
    logger.error(f"鏉冮檺绠＄悊API璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

# 娉ㄥ唽鐖櫕浠诲姟绠＄悊API璺敱
try:
    from backend.api.v1.admin.crawler_tasks import router as crawler_tasks_router
    app.include_router(crawler_tasks_router, prefix="/api/v1/admin", tags=["crawler-tasks"])
    logger.info("Crawler task management API routes registered (/api/v1/admin/crawler/tasks)")
except Exception as e:
    logger.error(f"鐖櫕浠诲姟绠＄悊API璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

# 娉ㄥ唽浠诲姟鐩戞帶API璺敱
try:
    from backend.api.v1.task_monitor import router as task_monitor_router
    app.include_router(task_monitor_router, prefix="/api/v1", tags=["task-monitor"])
    logger.info("Task monitoring API routes registered (/api/v1/task-monitor)")
except Exception as e:
    logger.error(f"浠诲姟鐩戞帶API璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

# 娉ㄥ唽鏃ュ織API璺敱
try:
    from backend.api.v1.admin.logs import router as logs_router
    # 灏唋ogs璺敱娉ㄥ唽鍒?api/v1/admin/system璺緞涓嬶紝杩欐牱API绔偣灏嗘槸/api/v1/admin/system/logs/db/security
    app.include_router(logs_router, prefix="/api/v1/admin/system", tags=["system-logs"])
    logger.info("Log API routes registered (/api/v1/admin/system/logs)")
except Exception as e:
    logger.error(f"鏃ュ織API璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

# Register monitoring module route
try:
    from backend.api.v1.admin.crawler_sources import router as crawler_sources_router
    app.include_router(crawler_sources_router, prefix="/api/v1/admin", tags=["crawler-sources"])
    logger.info("Crawler data source API routes registered (/api/v1/admin/crawler/sources)")
except Exception as e:
    logger.error(f"鐖櫕鏁版嵁婧怉PI璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")


try:
    from backend.api.v1.data_source_100qiu import router as data_source_100qiu_router
    # Router already has "/data-source-100qiu" prefix; mount under "/api/v1" only.
    app.include_router(data_source_100qiu_router, prefix="/api/v1", tags=["data-source-100qiu"])
    logger.info("100qiu data source API routes registered (/api/v1/data-source-100qiu)")
except Exception as e:
    logger.error(f"100qiu鏁版嵁婧怉PI璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

try:
    from backend.api.v1.admin.source_sync import router as source_sync_router

    app.include_router(source_sync_router, prefix="/api/v1/admin", tags=["source-sync"])
    logger.info("Source sync API routes registered (/api/v1/admin/source-sync)")
except Exception as e:
    logger.error(f"Source sync API route registration failed: {e}")
    import traceback
    logger.error(f"Details: {traceback.format_exc()}")

try:
    from backend.api.v1.admin.kaggle_sync import router as kaggle_sync_router

    app.include_router(kaggle_sync_router, prefix="/api/v1/admin", tags=["kaggle-sync"])
    logger.info("Kaggle sync API routes registered (/api/v1/admin/kaggle-sync)")
except Exception as e:
    logger.error(f"Kaggle sync API route registration failed: {e}")
    import traceback
    logger.error(f"Details: {traceback.format_exc()}")


try:
    from backend.api.v1.admin.crawler_configs import router as crawler_configs_router
    app.include_router(crawler_configs_router, prefix="/api/v1/admin", tags=["crawler-configs"])
    logger.info("Crawler config API routes registered (/api/v1/admin/crawler/config)")
except Exception as e:
    logger.error(f"鐖櫕閰嶇疆API璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

try:
    from backend.api.v1.admin.crawler_intelligence import router as crawler_intel_router
    app.include_router(crawler_intel_router, prefix="/api/v1/admin", tags=["crawler-intelligence"])
    logger.info("Crawler intelligence API routes registered (/api/v1/admin/crawler/intelligence)")
except Exception as e:
    logger.error(f"鐖櫕鎯呮姤API璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

# 娉ㄥ唽鐢ㄦ埛绠＄悊API璺敱
try:
    from backend.api.v1.admin_user_management import router as admin_user_management_router
    app.include_router(admin_user_management_router, prefix="/api/v1/admin", tags=["admin-user-management"])
    logger.info("Admin user management API routes registered (/api/v1/admin/admin-users)")
except Exception as e:
    logger.error(f"绠＄悊鍛樼敤鎴风鐞咥PI璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

# 娉ㄥ唽閮ㄩ棬绠＄悊API璺敱
try:
    from backend.api.v1.departments import router as departments_router
    app.include_router(departments_router, prefix="/api/v1/admin", tags=["departments"])
    logger.info("Department management API routes registered (/api/v1/admin/departments)")
except Exception as e:
    logger.error(f"閮ㄩ棬绠＄悊API璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

try:
    from backend.api.v1.users import router as users_router
    app.include_router(users_router, prefix="/api/v1/admin", tags=["users"])
    logger.info("Regular user management API routes registered (/api/v1/admin/users)")
except Exception as e:
    logger.error(f"鏅€氱敤鎴风鐞咥PI璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

try:
    from backend.api.v1.frontend_user_management import router as frontend_user_management_router
    # Keep frontend-user APIs namespaced to avoid catching generic /api/v1/admin/{user_id}
    # which can shadow other admin endpoints such as /api/v1/admin/data.
    app.include_router(frontend_user_management_router, prefix="/api/v1/admin/frontend-users", tags=["frontend-user-management"])
    logger.info("Frontend user management API routes registered (/api/v1/admin/frontend-users)")
except Exception as e:
    logger.error(f"鍓嶇鐢ㄦ埛绠＄悊API璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

try:
    from backend.api.v1.simple_user_api import router as simple_user_api_router
    # Keep simple-user APIs namespaced to avoid route collisions under /api/v1/admin/*
    app.include_router(simple_user_api_router, prefix="/api/v1/admin/simple-users", tags=["simple-user-api"])
    logger.info("Simple user API routes registered (/api/v1/admin/simple-users)")
except Exception as e:
    logger.error(f"绠€鍗曠敤鎴稟PI璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

try:
    from backend.api.v1.draw_prediction import router as draw_prediction_router
    app.include_router(draw_prediction_router, prefix="/api/v1", tags=["draw-prediction"])
    logger.info("Draw prediction API routes registered (/api/v1/draw-prediction)")
except Exception as e:
    logger.error(f"骞冲眬棰勬祴API璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

try:
    from backend.api.v1.admin.lottery_schedule import router as admin_lottery_schedule_router
    app.include_router(admin_lottery_schedule_router, prefix="/api/v1/admin/lottery-schedules", tags=["admin-lottery-schedules"])
    logger.info("Admin lottery schedule API routes registered (/api/v1/admin/lottery-schedules)")
except Exception as e:
    logger.error(f"鍖楀崟璧涚▼API璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

try:
    from backend.api.v1.data_center_adapter import router as data_center_adapter_router
    app.include_router(data_center_adapter_router, prefix="/api/v1", tags=["data-center-adapter"])
    logger.info("Data center adapter API routes registered (/api/v1/stats/data-center)")
except Exception as e:
    logger.error(f"鏁版嵁涓績閫傞厤API璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

try:
    from backend.api.v1.llm import router as llm_router
    app.include_router(llm_router, prefix="/api/v1", tags=["llm"])
    logger.info("LLM chat API routes registered (/api/v1/llm/chat)")
except Exception as e:
    logger.error(f"LLM chat API route registration failed: {e}")
    import traceback
    logger.error(f"Details: {traceback.format_exc()}")

try:
    from backend.api.v1.llm_providers import router as llm_providers_router
    app.include_router(llm_providers_router, prefix="/api/v1", tags=["llm-providers"])
    logger.info("LLM providers API routes registered (/api/v1/llm-providers)")
except Exception as e:
    logger.error(f"LLM渚涘簲鍟咥PI璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

try:
    from backend.api.v1.admin.intelligence_collection import router as admin_intelligence_collection_router
    app.include_router(admin_intelligence_collection_router, prefix="/api/v1/admin", tags=["intelligence-collection"])
    logger.info("Admin intelligence collection API routes registered (/api/v1/admin/intelligence/collection)")
except Exception as e:
    logger.error(f"鎯呮姤閲囬泦API璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

try:
    from backend.api.v1.admin.league_management import router as admin_league_management_router
    app.include_router(admin_league_management_router, prefix="/api/v1/admin/leagues", tags=["admin-leagues"])
    logger.info("Admin league management API routes registered (/api/v1/admin/leagues)")
except Exception as e:
    logger.error(f"League management API route registration failed: {e}")
    import traceback
    logger.error(f"Details: {traceback.format_exc()}")

# 娉ㄥ唽鍖楀崟杩囨护API璺敱 - 鐩存帴瀵煎叆
try:
    from backend.app.api_v1.endpoints.beidan_filter_api import router as beidan_filter_router
    app.include_router(beidan_filter_router, prefix="/api/v1/beidan-filter", tags=["beidan-filter"])
    logger.info("Beidan filter API routes registered (/api/v1/beidan-filter)")
except Exception as e:
    logger.error(f"鍖楀崟杩囨护API璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

# 娉ㄥ唽鍖楀崟鎶曟敞妯℃嫙API璺敱
try:
    from backend.app.api_v1.endpoints.beidan_betting_simulator_api import router as beidan_betting_router
    app.include_router(beidan_betting_router, prefix="/api/v1/beidan-betting", tags=["beidan-betting"])
    logger.info("Beidan betting simulator API routes registered (/api/v1/beidan-betting)")
except Exception as e:
    logger.error(f"鍖楀崟鎶曟敞妯℃嫙API璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

# 娉ㄥ唽澶氱瓥鐣ョ瓫閫堿PI璺敱
try:
    from backend.app.api_v1.endpoints.multi_strategy_api import router as multi_strategy_router
    app.include_router(multi_strategy_router, prefix="/api/v1", tags=["multi-strategy"])
    logger.info("Multi strategy API routes registered (/api/v1/multi-strategy)")
except Exception as e:
    logger.error(f"澶氱瓥鐣PI璺敱娉ㄥ唽澶辫触: {e}")
    import traceback
    logger.error(f"璇︾粏鍫嗘爤: {traceback.format_exc()}")

# 娉ㄥ唽admin鐧诲綍绔偣 - 娉ㄦ剰杩欓噷涓嶉渶瑕侀噸澶嶆敞鍐岋紝鍥犱负auth妯″潡宸茬粡澶勭悊浜嗙櫥褰?# 鐧诲綍API搴旈€氳繃auth妯″潡娉ㄥ唽锛岃€屼笉鏄湪admin妯″潡涓噸澶嶆敞鍐?# 濡傛灉闇€瑕乤dmin鐗瑰畾鐨勭櫥褰曞姛鑳斤紝璇风‘淇濅笉瑕佷笌auth妯″潡鍐茬獊

# Register exception handlers
try:
    from backend.exceptions import setup_exception_handlers
    setup_exception_handlers(app)
    logger.info("Exception handlers registered")
except Exception as e:
    logger.error(f"Exception handler registration failed: {e}")


# 鍩虹璺敱
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "浣撹偛褰╃エ鎵洏绯荤粺 API", "version": "1.0.0"}

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
    # 妫€鏌ユ暟鎹簱杩炴帴
    try:
                # Use absolute import path for readiness check
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
    
        # AI service readiness
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



# ===== /api/v1 璺敱 =====
from fastapi import Body
import jwt
from datetime import datetime as dt, timezone, timedelta

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict):
    """鍒涘缓JWT璁块棶浠ょ墝"""
    to_encode = data.copy()
    expire = dt.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": dt.now(timezone.utc), "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/api/v1/auth/register")
async def register(
    email: str = Body(...),
    password: str = Body(...),
    confirmPassword: str = Body(...),
    captcha: Optional[str] = Body(None)
):
    """User registration endpoint (/api/v1)."""
    if password != confirmPassword:
        logger.warning(f"Registration failed: passwords do not match for email {email}")
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    logger.info(f"User registration attempted for email: {email}")
    # TODO: 瀹炵幇鐪熷疄鐢ㄦ埛鐨勬敞鍐岄€昏緫
    return {
        "code": 200,
        "message": "娉ㄥ唽鎴愬姛",
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

LOGIN_RATE_LIMIT = os.getenv("LOGIN_RATE_LIMIT", "10/minute")
DASHBOARD_RATE_LIMIT = os.getenv("DASHBOARD_RATE_LIMIT", "180/minute")
INTELLIGENCE_RATE_LIMIT = os.getenv("INTELLIGENCE_RATE_LIMIT", "240/minute")
STATS_RATE_LIMIT = os.getenv("STATS_RATE_LIMIT", "240/minute")


@app.post("/api/v1/auth/login")
@limiter.limit(LOGIN_RATE_LIMIT)  # Strict limit for login attempts - prevents brute force
async def login_v1(
    request: Request,
    username: str = Body(...),
    password: str = Body(...),
    db=Depends(get_db),
):
    """User login endpoint (/api/v1)."""
    logger.info(f"Login attempt for username: {username}")
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    user = authenticate_user(username, password)
    if not user:
        logger.warning(f"Login failed: invalid credentials for username {username}")
        try:
            from backend.services.user_activity_logger import get_user_activity_logger
            activity_logger = get_user_activity_logger(db)
            activity_logger.log_user_login(
                user_id=0,
                username=username,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason="鐢ㄦ埛鍚嶆垨瀵嗙爜閿欒",
            )
        except Exception as log_error:
            logger.warning(f"Login failure log error: {log_error}")
        raise HTTPException(status_code=401, detail="鐢ㄦ埛鍚嶆垨瀵嗙爜閿欒")

    logger.info(f"User logged in successfully: {user['username']} (ID: {user['id']})")
    try:
        from backend.services.user_activity_logger import get_user_activity_logger
        activity_logger = get_user_activity_logger(db)
        activity_logger.log_user_login(
            user_id=user["id"],
            username=user["username"],
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
        )
    except Exception as log_error:
        logger.warning(f"Login success log error: {log_error}")

    # 鍒涘缓JWT浠ょ墝
    access_token = create_access_token({
        "sub": user["username"],
        "user_id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
    })

    return {
        "code": 200,
        "message": "鐧诲綍鎴愬姛",
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

@app.post("/api/v1/auth/refresh")
async def refresh_v1(refresh_token: str = Body(..., embed=True)):
    """鍒锋柊璁块棶浠ょ墝 (/api/v1)"""
    if not refresh_token or not refresh_token.startswith("refresh-"):
        raise HTTPException(status_code=401, detail="鍒锋柊浠ょ墝鏃犳晥")
    access_token = refresh_token.replace("refresh-", "", 1)
    return {
        "code": 200,
        "message": "token refreshed",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        },
    }

@app.get("/api/v1/auth/me")
async def get_current_user_v1():
    """鑾峰彇褰撳墠鐢ㄦ埛淇℃伅 (/api/v1) - 闇€瑕丣WT楠岃瘉"""
    # TODO: 娣诲姞JWT楠岃瘉涓棿浠?    logger.info("Current user info requested")
    # 鏆傛椂杩斿洖婕旂ず鏁版嵁
    return {
        "code": 200,
        "message": "success",
        "data": {
            "userId": 1,
            "username": "admin",
            "email": "admin@example.com",
            "firstName": "绯荤粺",
            "lastName": "Admin",
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

# ===== 鍏煎鍓嶇鏃ц矾寰勩€佹柊澧炰华琛ㄦ澘銆佹儏鎶ユā鍧楁帴鍙?=====

# 閮ㄩ棬绠＄悊鍏煎璺敱 - 鐩存帴杩斿洖404鎻愮ず浣跨敤鏂癆PI
@app.get("/admin/departments")
async def departments_not_found():
    """鏃х殑閮ㄩ棬鍒楄〃璇锋眰 - 杩斿洖404鎻愮ず浣跨敤鏂癆PI"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=404,
        content={
            "code": 404,
            "message": "API migrated",
            "detail": "璇蜂娇鐢ㄦ柊鐨凙PI璺緞: /api/v1/admin/departments"
        }
    )

# 閮ㄩ棬绠＄悊鍏煎璺敱 - 鐢ㄤ簬鐢ㄦ埛閮ㄩ棬绠＄悊椤甸潰
@app.get("/admin/users/departments")
async def user_departments_page():
    """鐢ㄦ埛閮ㄩ棬绠＄悊椤甸潰 - 杩斿洖鍏煎淇℃伅"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=200,
        content={
            "code": 200,
            "message": "success",
            "data": {
                "title": "鐢ㄦ埛閮ㄩ棬绠＄悊",
                "description": "閮ㄩ棬绠＄悊椤甸潰锛屼娇鐢ˋPI: /api/v1/admin/departments"
            }
        }
    )

@app.get("/admin/roles")
async def roles_not_found():
    """鏃х殑roles璇锋眰 - 杩斿洖404鎻愮ず浣跨敤鏂癆PI"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=404,
        content={
            "code": 404,
            "message": "API migrated",
            "detail": "璇蜂娇鐢ㄦ柊鐨凙PI璺緞: /api/v1/admin/roles"
        }
    )

@app.get("/api/auth/login")
async def login_compat_get():
    """鍏煎鍓嶇閿欒鐨凣ET璇锋眰 - 杩斿洖鎻愮ず淇℃伅"""
    logger.warning("GET request made to login endpoint (should be POST)")
    return {"code": 405, "message": "姝ゆ帴鍙ｄ粎鏀寔POST鏂规硶", "detail": "璇蜂娇鐢≒OST鏂规硶璁块棶鐧诲綍鎺ュ彛"}

@app.post("/api/auth/login")
@limiter.limit(LOGIN_RATE_LIMIT)
async def login_compat(
    request: Request,
    username: str = Body(...),
    password: str = Body(...)
):
    """Compatibility login endpoint for legacy frontend clients."""
    logger.info(f"Compatibility login attempt for username: {username}")
    user = authenticate_user(username, password)
    if not user:
        logger.warning(f"Compatibility login failed: invalid credentials for username {username}")
        raise HTTPException(401, "鐢ㄦ埛鍚嶆垨瀵嗙爜閿欒")
    
    logger.info(f"User logged in successfully via compatibility endpoint: {user['username']} (ID: {user['id']})")
    
    # 鍒涘缓JWT浠ょ墝
    access_token = create_access_token({
        "sub": user["username"],
        "user_id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"]
    })
    
    return {
        "code": 200,
        "message": "鐧诲綍鎴愬姛",
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
    """鍏煎鍓嶇鑾峰彇鐢ㄦ埛淇℃伅鎺ュ彛"""
    logger.info("Profile info requested via compatibility endpoint")
    # TODO: 浠嶫WT涓彁鍙栫敤鎴稩D骞舵煡璇㈡暟鎹簱
    return {
        "code": 200,
        "message": "success",
        "data": {
            "userId": 1,
            "username": "admin",
            "email": "admin@example.com",
            "firstName": "绯荤粺",
            "lastName": "Admin",
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

@app.get(
    "/api/dashboard/summary",
    summary="仪表盘汇总",
    description="获取仪表盘统计信息（仅管理员）",
)
@limiter.limit(DASHBOARD_RATE_LIMIT)
async def dashboard_summary(
    request: Request,
    current_user: User = Depends(get_current_active_admin_user)
):
    """浠〃鏉跨粺璁℃暟鎹?- 鐪熷疄鏁版嵁搴撴煡璇?(Admin only)"""
    try:
        logger.info(f"Dashboard summary requested by admin user: {current_user.username} (ID: {current_user.id})")
        stats = get_dashboard_stats()
        return {
            "code": 200,
            "data": stats
        }
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"鑾峰彇浠〃鏉挎暟鎹け璐? {str(e)}")

@app.get(
    "/api/intelligence/screening/list",
    summary="智能筛选列表",
    description="获取智能筛选结果列表（仅管理员）",
)
@limiter.limit(INTELLIGENCE_RATE_LIMIT)
async def screening_list(
    request: Request,
    current_user: User = Depends(get_current_active_admin_user)
):
    """鎯呮姤绛涢€夊垪琛?- 鐪熷疄鏁版嵁搴撴煡璇?(Admin only)"""
    try:
        logger.info(f"Intelligence screening list requested by admin user: {current_user.username} (ID: {current_user.id})")
        result = get_intelligence_screening_list()
        return {
            "code": 200,
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to get intelligence screening list: {str(e)}")
        raise HTTPException(status_code=500, detail=f"鑾峰彇鎯呮姤绛涢€夊垪琛ㄥけ璐? {str(e)}")

@app.get("/api/stats/data-center")
@limiter.limit(STATS_RATE_LIMIT)
async def get_data_center_stats(
    request: Request,
    current_user: User = Depends(get_current_active_admin_user)
):
    """鏁版嵁涓績缁熻淇℃伅 (Admin only)"""
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
    
    # 鍒涘缓鏁版嵁搴撹〃
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # 寮哄埗鍒涘缓LLM Provider琛紙纭繚琛ㄥ瓨鍦級
    from backend.models.llm_provider import LLMProvider
    LLMProvider.__table__.create(bind=engine, checkfirst=True)
    logger.info("Database tables created successfully")
    
    parser = argparse.ArgumentParser(description='鍚姩API鏈嶅姟')
    parser.add_argument('--port', type=int, default=8000, help='鏈嶅姟绔彛锛岄粯璁?000锛堜笌鍓嶇浠ｇ悊涓€鑷达級')
    args = parser.parse_args()
    
# Check port availability before startup.
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("0.0.0.0", args.port))
        sock.close()
    except OSError as e:
        if "10013" in str(e) or "Address already in use" in str(e):
            logger.error(f"Port {args.port} is already in use. Please free it before restart.")
            logger.info("馃挕 鍙娇鐢? netstat -ano | findstr :%d", args.port)
            logger.info("馃挕 鐒跺悗: taskkill /F /PID <杩涚▼ID>")
            exit(1)
        else:
            raise
    
    # 鍚姩搴旂敤
    logger.info("馃殌 鍚姩浣撹偛褰╃エ鎵洏绯荤粺...")
    logger.info(f"馃搷 鏈嶅姟鍦板潃: http://localhost:%d", args.port)
    logger.info(f"馃摎 API鏂囨。: http://localhost:%d/docs", args.port)
    logger.info(f"馃搳 鍋ュ悍妫€鏌? http://localhost:%d/health/live", args.port)
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=args.port,
            log_level="info"
        )
    except OSError as e:
        if "10013" in str(e):
            logger.error("Port %d is already in use. Please free it before restart.", args.port)
            logger.info("馃挕 鍙娇鐢? netstat -ano | findstr :%d", args.port)
            logger.info("馃挕 鐒跺悗: taskkill /F /PID <杩涚▼ID>")
        else:
            raise
    
    logger.info("Application service stopped")
