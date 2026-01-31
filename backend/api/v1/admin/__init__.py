"""
Admin API v1 路由入口
"""
import logging
from fastapi import APIRouter

# 导入各个模块的路由
from . import logs
from . import metrics
from . import cache_management
from . import data_source
from . import odds_management
from . import lottery_schedule
from . import beidan_schedule

router = APIRouter()

# 包含各个管理模块的路由
router.include_router(logs.router, prefix="/logs", tags=["admin-logs"])
router.include_router(metrics.router, prefix="/metrics", tags=["admin-metrics"])
router.include_router(cache_management.router, prefix="/cache", tags=["admin-cache"])
router.include_router(data_source.router, prefix="/sources", tags=["admin-data-sources"])
router.include_router(odds_management.router, prefix="/odds", tags=["admin-odds"])
router.include_router(lottery_schedule.router, prefix="/lottery-schedules", tags=["admin-lottery-schedules"])
router.include_router(beidan_schedule.router, prefix="/beidan-schedules", tags=["admin-beidan-schedules"])

# 可选模块，如果存在则导入
try:
    from . import match_admin
    router.include_router(match_admin.router, prefix="/matches", tags=["admin-matches"])
except ImportError:
    logging.warning("match_admin module not available")

try:
    from . import league_management
    router.include_router(league_management.router, prefix="/leagues", tags=["admin-leagues"])
except ImportError:
    logging.warning("league_management module not available")

