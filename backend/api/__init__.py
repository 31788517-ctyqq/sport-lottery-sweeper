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
    """
    router = APIRouter()
    
    # 1. 加载 API v1 路由（最高优先级）
    try:
        from .v1 import router as v1_router
        router.include_router(v1_router)
        logger.info("API v1 路由已加载")
    except Exception as e:
        logger.error(f"API v1 路由加载失败: {e}")
    
    # 2. 加载 WebSocket 路由
    try:
        from .websocket_handler import router as ws_router
        router.include_router(ws_router, prefix="/ws", tags=["websocket"])
        logger.info("WebSocket 路由已加载")
    except Exception as e:
        logger.error(f"WebSocket 路由加载失败: {e}")
    
    logger.info("API路由器初始化完成，已移除所有废弃的向后兼容路由")
    
    return router


# 导出路由实例
router = create_api_router()

__all__ = ["router"]