"""
精简版API路由，只包含竞彩足球相关功能，用于快速启动
"""
from fastapi import APIRouter
from typing import Dict, Any


def create_minimal_api_router():
    """创建最小API路由器，仅包含竞彩足球功能"""
    router = APIRouter()

    # 直接在函数内定义路由，避免导入大量模块
    @router.get("/health")
    async def health_check() -> Dict[str, Any]:
        """健康检查端点"""
        return {"status": "healthy", "service": "sport-lottery-sweeper"}

    # 包含jczq_routes，这是核心功能
    try:
        from .jczq_routes import router as jczq_router
        router.include_router(jczq_router, prefix="", tags=["jczq"])
    except ImportError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to import jczq_routes: {e}")

    return router


# 创建最小API路由器实例
minimal_router = create_minimal_api_router()