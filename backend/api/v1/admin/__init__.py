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

# 可选模块，如果存在则导入
try:
    from . import odds_management
    from . import lottery_schedule
    from . import beidan_schedule
except ImportError as e:
    logging.warning(f"可选admin模块导入失败: {e}")

router = APIRouter()

# 包含各个管理模块的路由
router.include_router(logs.router, prefix="/logs", tags=["admin-logs"])
router.include_router(metrics.router, prefix="/metrics", tags=["admin-metrics"])
router.include_router(cache_management.router, prefix="/cache", tags=["admin-cache"])
router.include_router(data_source.router, prefix="/sources", tags=["admin-data-sources"])

# 包含可选模块路由
try:
    router.include_router(odds_management.router, prefix="/odds", tags=["admin-odds"])
    router.include_router(lottery_schedule.router, prefix="/lottery-schedules", tags=["admin-lottery-schedules"])
    router.include_router(beidan_schedule.router, prefix="/beidan-schedules", tags=["admin-beidan-schedules"])
except NameError:
    logging.warning("可选admin模块未加载")

# AI_WORKING: coder1 @2026-01-31 - 修正match_admin导入路径，确保北单赛程管理相关路由被正确注册
try:
    from ..match_admin import router as match_admin_router
    router.include_router(match_admin_router, prefix="/matches", tags=["admin-matches"])
    logging.info("match_admin路由已成功注册")
except ImportError as e:
    logging.warning(f"match_admin模块导入失败: {e}")
# AI_DONE: coder1 @2026-01-31

try:
    from . import league_management
    router.include_router(league_management.router, prefix="/leagues", tags=["admin-leagues"])
    logging.info("league_management路由已成功注册")
except ImportError as e:
    logging.warning(f"league_management module not available: {e}")

# 任务管理路由
# 注释掉：已在main.py中手动注册以避免路径重复

try:
    from . import system_monitor
    router.include_router(system_monitor.router, prefix="/system/monitor", tags=["admin-system-monitor"])
except ImportError as e:
    logging.warning(f"system_monitor模块导入失败: {e}")
