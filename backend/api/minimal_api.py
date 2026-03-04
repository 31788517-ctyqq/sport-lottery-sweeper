"""
精简版API路由，只包含竞彩足球相关功能，用于快速启动
"""
from fastapi import APIRouter
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def create_minimal_api_router():
    """创建最小API路由器，仅包含竞彩足球功能"""
    router = APIRouter()

    # 直接在函数内定义路由，避免导入大量模块
    @router.get("/health")
    async def health_check() -> Dict[str, Any]:
        """健康检查端点"""
        return {"status": "healthy", "service": "sport-lottery-sweeper"}

    # 注意：jczq_routes已废弃，不再包含在此版本中
    # 使用新版API: /api/v1/jczq/*
    logger.info("精简版API已加载，使用新版API端点")

    return router


# 创建最小API路由器实例
minimal_router = create_minimal_api_router()