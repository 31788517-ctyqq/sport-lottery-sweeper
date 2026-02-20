"""
Admin API v1 路由入口
"""
import logging
from fastapi import APIRouter

from . import logs
from . import metrics
from . import cache_management
from . import data_source

router = APIRouter()

router.include_router(logs.router, prefix="/logs", tags=["admin-logs"])
router.include_router(metrics.router, prefix="/metrics", tags=["admin-metrics"])
router.include_router(cache_management.router, prefix="/cache", tags=["admin-cache"])
router.include_router(data_source.router, prefix="", tags=["admin-data-sources"])

# Optional modules
try:
    from . import odds_management
    router.include_router(odds_management.router, prefix="/odds", tags=["admin-odds"])
except ImportError as e:
    logging.warning(f"optional module odds_management not loaded: {e}")

try:
    from . import lottery_schedule
    router.include_router(lottery_schedule.router, prefix="/lottery-schedules", tags=["admin-lottery-schedules"])
except ImportError as e:
    logging.warning(f"optional module lottery_schedule not loaded: {e}")

try:
    from . import beidan_schedule
    router.include_router(beidan_schedule.router, prefix="/beidan-schedules", tags=["admin-beidan-schedules"])
except ImportError as e:
    logging.warning(f"optional module beidan_schedule not loaded: {e}")

# Re-enable intelligence collection routes
try:
    from . import intelligence_collection
    router.include_router(intelligence_collection.router, prefix="", tags=["admin-intelligence-collection"])
except ImportError as e:
    logging.warning(f"optional module intelligence_collection not loaded: {e}")

try:
    from ..match_admin import router as match_admin_router
    router.include_router(match_admin_router, prefix="/matches", tags=["admin-matches"])
except ImportError as e:
    logging.warning(f"match_admin module not available: {e}")

try:
    from . import league_management
    router.include_router(league_management.router, prefix="/leagues", tags=["admin-leagues"])
except ImportError as e:
    logging.warning(f"league_management module not available: {e}")

try:
    from . import system_monitor
    router.include_router(system_monitor.router, prefix="/system/monitor", tags=["admin-system-monitor"])
except ImportError as e:
    logging.warning(f"system_monitor module not available: {e}")
