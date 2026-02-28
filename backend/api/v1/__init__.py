from fastapi import FastAPI
from fastapi.routing import APIRoute
from typing import List
import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

# 定义API路由器
router = APIRouter()

def register_routers(app: FastAPI):
    """
    Register all routers under this package to the app
    """
    # Import all modules containing routers to ensure they are registered
    try:
        from . import admin
        logger.info("Admin module loaded successfully")
    except ImportError as e:
        logger.error(f"FAILED admin module import: {e}")
    except Exception as e:
        logger.error(f"admin module import error: {e}")

    # 尝试导入entity_mapping模块
    try:
        from .admin import entity_mapping
        # 将路由器添加到应用
        app.include_router(
            entity_mapping.router,
            prefix="/entity-mapping",
            tags=["entity-mapping"]
        )
        logger.info("Entity mapping module loaded successfully")
    except ImportError as e:
        logger.error(f"FAILED entity mapping module import: {e}")
    except Exception as e:
        logger.error(f"entity mapping module import error: {e}")

    try:
        from . import auth
        logger.info("Auth module loaded successfully")
    except ImportError as e:
        logger.error(f"FAILED auth module import: {e}")
    except Exception as e:
        logger.error(f"auth module import error: {e}")

    try:
        from . import lottery_schedule
        logger.info("Lottery schedule module loaded successfully")
    except ImportError as e:
        logger.error(f"FAILED lottery_schedule module import: {e}")
    except Exception as e:
        logger.error(f"lottery_schedule module import error: {e}")

    try:
        from . import lottery_simple
        logger.info("Lottery simple module loaded successfully")
    except ImportError as e:
        logger.error(f"FAILED lottery_simple module import: {e}")
    except Exception as e:
        logger.error(f"lottery_simple module import error: {e}")

    try:
        from . import lottery_direct
        logger.info("Lottery direct module loaded successfully")
    except ImportError as e:
        logger.error(f"FAILED lottery_direct module import: {e}")
    except Exception as e:
        logger.error(f"lottery_direct module import error: {e}")

    try:
        from . import lottery
        logger.info("Lottery module loaded successfully")
    except ImportError as e:
        logger.error(f"lottery module import failed: {e}")
    except Exception as e:
        logger.error(f"lottery module import error: {e}")

    try:
        from . import matches
        logger.info("Matches module loaded successfully")
    except ImportError as e:
        logger.error(f"matches module import failed: {e}")
    except Exception as e:
        logger.error(f"matches module import error: {e}")

    try:
        from . import public_matches
        logger.info("Public matches module loaded successfully")
    except ImportError as e:
        logger.error(f"public_matches module import failed: {e}")
    except Exception as e:
        logger.error(f"public_matches module import error: {e}")

    try:
        from . import draw_prediction
        logger.info("Draw prediction module loaded successfully")
    except ImportError as e:
        logger.error(f"FAILED draw_prediction module import: {e}")
    except Exception as e:
        logger.error(f"draw_prediction module import error: {e}")

    try:
        from . import hedging
        logger.info("Hedging module loaded successfully")
    except ImportError as e:
        logger.error(f"FAILED hedging module import: {e}")
    except Exception as e:
        logger.error(f"hedging module import error: {e}")

    try:
        from . import crawler
        logger.info("Crawler module loaded successfully")
    except ImportError as e:
        logger.error(f"FAILED crawler module import: {e}")
    except Exception as e:
        logger.error(f"crawler module import error: {e}")

    try:
        from . import crawler_alert
        logger.info("Crawler alert module loaded successfully")
    except ImportError as e:
        logger.error(f"FAILED crawler_alert module import: {e}")
    except Exception as e:
        logger.error(f"crawler_alert module import error: {e}")

    try:
        from . import crawler_monitor
        logger.info("Crawler monitor module loaded successfully")
    except ImportError as e:
        logger.error(f"FAILED crawler_monitor module import: {e}")
    except Exception as e:
        logger.error(f"crawler_monitor module import error: {e}")

    try:
        from . import crawler_tasks_adapter
        logger.info("Crawler tasks adapter module loaded successfully")
    except ImportError as e:
        logger.error(f"FAILED crawler_tasks_adapter module import: {e}")
    except Exception as e:
        logger.error(f"crawler_tasks_adapter module import error: {e}")

    try:
        from . import data_center_adapter
        logger.info("Data center adapter module loaded successfully")
    except ImportError as e:
        logger.error(f"FAILED data_center_adapter module import: {e}")
    except Exception as e:
        logger.error(f"data_center_adapter module import error: {e}")

    try:
        from . import headers_adapter
        logger.info("Headers adapter module loaded successfully")
    except ImportError as e:
        logger.error(f"FAILED headers_adapter module import: {e}")
    except Exception as e:
        logger.error(f"headers_adapter module import error: {e}")

    try:
        from . import ip_pool_adapter
        logger.info("IP pool adapter module loaded successfully")
    except ImportError as e:
        logger.error(f"FAILED ip_pool_adapter module import: {e}")
    except Exception as e:
        logger.error(f"ip_pool_adapter module import error: {e}")

    try:
        from . import llm
        logger.info("LLM module loaded successfully")
    except ImportError as e:
        logger.error(f"FAILED llm module import: {e}")
    except Exception as e:
        logger.error(f"llm module import error: {e}")

    try:
        from . import llm_providers
        logger.info("LLM providers module loaded successfully")
    except ImportError as e:
        logger.error(f"FAILED llm_providers module import: {e}")
    except Exception as e:
        logger.error(f"llm_providers module import error: {e}")

    try:
        from . import log_analysis
        logger.info("Log analysis module loaded successfully")
    except ImportError as e:
        logger.error(f"FAILED log_analysis module import: {e}")
    except Exception as e:
        logger.error(f"log_analysis module import error: {e}")

    try:
        from . import data_source_100qiu
        logger.info("Data source 100qiu module loaded successfully")
    except ImportError as e:
        logger.error(f"FAILED data_source_100qiu module import: {e}")
    except Exception as e:
        logger.error(f"data_source_100qiu module import error: {e}")

    # 尝试获取所有注册的路由并打印
    routes: List[APIRoute] = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            routes.append(route)

    logger.info(f"Total registered routes: {len(routes)}")
    # 仅在调试模式下打印所有路由
    # for route in routes:
    #     logger.debug(f"Registered route: {route.methods} {route.path} -> {route.name}")