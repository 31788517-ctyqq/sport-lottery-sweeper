"""
API v1 router entrypoint.
"""
from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

# Main router
router = APIRouter()

# Import and register routes safely
try:
    from . import lottery
    logger.info("lottery module imported successfully")
except Exception as e:
    logger.error(f"lottery module import failed: {e}")

try:
    from . import matches
    logger.info("matches module imported successfully")
    router.include_router(matches.router, prefix="/matches", tags=["matches"])
except Exception as e:
    logger.error(f"matches module import failed: {e}")

try:
    from . import public_matches
    logger.info("public_matches module imported successfully")
    router.include_router(public_matches.router, prefix="/public-matches", tags=["public-matches"])
except Exception as e:
    logger.error(f"public_matches module import failed: {e}")

try:
    from . import admin
    logger.info("admin module imported successfully")
    router.include_router(admin.router, prefix="/admin")
except Exception as e:
    logger.error(f"admin module import failed: {e}")

try:
    from . import auth
    logger.info("SUCCESS auth module imported")
    logger.info(f"  auth.router: {auth.router}")
    logger.info(f"  auth.router routes: {len(auth.router.routes)}")
    router.include_router(auth.router)
except Exception as e:
    logger.error(f"FAILED auth module import: {e}")
    import traceback
    traceback.print_exc()

try:
    from . import intelligence
    logger.info("SUCCESS intelligence module imported")
except Exception as e:
    logger.error(f"FAILED intelligence module import: {e}")

try:
    from . import data_submission
    logger.info("SUCCESS data_submission module imported")
except Exception as e:
    logger.error(f"FAILED data_submission module import: {e}")

try:
    from . import caipiao_data
    logger.info("SUCCESS caipiao_data module imported")
    logger.info(f"  caipiao_data.router: {caipiao_data.router}")
    logger.info(f"  caipiao_data.router routes: {len(caipiao_data.router.routes)}")
except Exception as e:
    logger.error(f"FAILED caipiao_data module import: {e}")

try:
    from . import draw_prediction
    logger.info("SUCCESS draw_prediction module imported")
    router.include_router(draw_prediction.router)
except Exception as e:
    logger.error(f"FAILED draw_prediction module import: {e}")

try:
    from . import hedging
    logger.info("SUCCESS hedging module imported")
except Exception as e:
    logger.error(f"FAILED hedging module import: {e}")

try:
    from . import crawler
    logger.info("SUCCESS crawler module imported")
except Exception as e:
    logger.error(f"FAILED crawler module import: {e}")

try:
    from . import crawler_alert
    logger.info("SUCCESS crawler_alert module imported")
except Exception as e:
    logger.error(f"FAILED crawler_alert module import: {e}")

try:
    from . import crawler_monitor
    logger.info("SUCCESS crawler_monitor module imported")
except Exception as e:
    logger.error(f"FAILED crawler_monitor module import: {e}")

try:
    from . import crawler_tasks_adapter
    logger.info("SUCCESS crawler_tasks_adapter module imported")
except Exception as e:
    logger.error(f"FAILED crawler_tasks_adapter module import: {e}")

try:
    from . import data_center_adapter
    logger.info("SUCCESS data_center_adapter module imported")
    router.include_router(data_center_adapter.router, tags=["data-center-adapter"])
    logger.info("SUCCESS data_center_adapter routes registered")
except Exception as e:
    logger.error(f"FAILED data_center_adapter module import: {e}")

try:
    from . import headers_adapter
    logger.info("SUCCESS headers_adapter module imported")
except Exception as e:
    logger.error(f"FAILED headers_adapter module import: {e}")

try:
    from . import ip_pool_adapter
    logger.info("SUCCESS ip_pool_adapter module imported")
except Exception as e:
    logger.error(f"FAILED ip_pool_adapter module import: {e}")

try:
    from . import llm
    logger.info("SUCCESS llm module imported")
    logger.info(f"  llm.router: {llm.router}")
    logger.info(f"  llm.router routes: {len(llm.router.routes)}")
    router.include_router(llm.router)
except Exception as e:
    logger.error(f"FAILED llm module import: {e}")
    import traceback
    traceback.print_exc()

try:
    from . import llm_providers
    logger.info("SUCCESS llm_providers module imported")
    logger.info(f"  llm_providers.router: {llm_providers.router}")
    logger.info(f"  llm_providers.router routes: {len(llm_providers.router.routes)}")
    router.include_router(llm_providers.router)
except Exception as e:
    logger.error(f"FAILED llm_providers module import: {e}")
    import traceback
    traceback.print_exc()

try:
    from . import log_analysis
    logger.info("SUCCESS log_analysis module imported")
except Exception as e:
    logger.error(f"FAILED log_analysis module import: {e}")

try:
    from . import lottery_schedule
    logger.info("SUCCESS lottery_schedule module imported")
except Exception as e:
    logger.error(f"FAILED lottery_schedule module import: {e}")

try:
    from . import lottery_simple
    logger.info("SUCCESS lottery_simple module imported")
except Exception as e:
    logger.error(f"FAILED lottery_simple module import: {e}")

try:
    from . import lottery_test
    logger.info("SUCCESS lottery_test module imported")
except Exception as e:
    logger.error(f"FAILED lottery_test module import: {e}")

try:
    from . import lottery_direct
    logger.info("SUCCESS lottery_direct module imported")
except Exception as e:
    logger.error(f"FAILED lottery_direct module import: {e}")

try:
    from . import lottery_final
    logger.info("SUCCESS lottery_final module imported")
except Exception as e:
    logger.error(f"FAILED lottery_final module import: {e}")

try:
    from . import data_source_100qiu
    logger.info("SUCCESS data_source_100qiu module imported")
    logger.info(f"  data_source_100qiu.router: {data_source_100qiu.router}")
    logger.info(f"  data_source_100qiu.router routes: {len(data_source_100qiu.router.routes)}")
    router.include_router(data_source_100qiu.router)
except Exception as e:
    logger.error(f"FAILED data_source_100qiu module import: {e}")
    import traceback
    traceback.print_exc()

# Unified matches (optional)
logger.info("Registering unified_matches routes (optional)")
try:
    from . import unified_matches
    logger.info("SUCCESS unified_matches module imported")
    logger.info(f"  unified_matches.router: {unified_matches.router}")
    logger.info(f"  unified_matches.router routes: {len(unified_matches.router.routes)}")
    router.include_router(unified_matches.router)
    logger.info("SUCCESS unified_matches routes registered")
except Exception as e:
    logger.warning(f"Skipping unified_matches: {e}")

logger.info(f"API v1 router initialized. Routes: {len(router.routes)}")

__all__ = ["router"]

# Health endpoint
@router.get("/health")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "api_version": "v1",
        "endpoints": "dynamic",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }

# API info endpoint
@router.get("/info")
async def api_info() -> dict:
    return {
        "title": "体育彩票扫盘系统 API v1",
        "version": "1.0.0",
        "description": "提供体育彩票数据分析、预测和智能分析服务",
        "features": [
            "数据采集和分析",
            "比赛结果预测",
            "智能分析引擎",
            "实时监控分析",
            "LLM智能服务"
        ],
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }
