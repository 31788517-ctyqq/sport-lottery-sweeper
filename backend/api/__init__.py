"""
API routes package for Sport Lottery Sweeper
优化后的统一路由管理
"""
from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)


def create_api_router():
    """
    创建优化的API路由器
    
    路由优先级（从高到低）：
    1. API v1 - 新版标准API (/api/v1/*)
    2. WebSocket - 实时通信 (/api/v1/ws/*)
    3. 向后兼容路由 - 遗留API (/api/v1/jczq/* - 已废弃)
    """
    router = APIRouter()
    
    # 1. 加载 API v1 路由（最高优先级）
    try:
        from .v1 import router as v1_router
        router.include_router(v1_router)
        logger.info("✓ API v1 路由已加载")
    except Exception as e:
        logger.error(f"✗ API v1 路由加载失败: {e}")
    
    # 2. 加载 WebSocket 路由
    try:
        from .websocket import router as ws_router
        router.include_router(ws_router, prefix="/ws", tags=["websocket"])
        logger.info("✓ WebSocket 路由已加载")
    except Exception as e:
        logger.error(f"✗ WebSocket 路由加载失败: {e}")
    
    # 3. 向后兼容路由（已废弃，计划在 v2.0 移除）
    try:
        from .jczq_routes import router as legacy_jczq_router
        router.include_router(
            legacy_jczq_router, 
            tags=["legacy-deprecated"],
            deprecated=True
        )
        logger.warning("⚠ 向后兼容路由已加载（已废弃）")
    except Exception as e:
        logger.info(f"向后兼容路由未加载: {e}")

    return router


# 导出路由实例
router = create_api_router()

__all__ = ["router"]