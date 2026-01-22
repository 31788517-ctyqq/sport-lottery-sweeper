"""
API v1 初始化
"""
from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

def create_api_router():
    """
    创建并注册所有API v1路由
    
    Returns:
        APIRouter: 包含所有v1路由的路由器对象
    """
    router = APIRouter()

    # 用户认证相关路由
    try:
        from .auth import router as auth_router
        router.include_router(auth_router, prefix="/auth", tags=["auth"])
        logger.info("API v1 - auth 路由已注册")
    except Exception as e:
        logger.error(f"API v1 - auth 路由注册失败: {e}")

    # 管理员相关路由
    try:
        from .admin import router as admin_router
        router.include_router(admin_router, prefix="/admin", tags=["admin"])
        logger.info("API v1 - admin 路由已注册")
    except Exception as e:
        logger.error(f"API v1 - admin 路由注册失败: {e}")

    # 管理员用户管理相关路由
    try:
        from .admin_user_management import router as admin_user_router
        router.include_router(admin_user_router, prefix="/admin/users", tags=["admin"])
        logger.info("API v1 - admin_user_management 路由已注册")
    except Exception as e:
        logger.error(f"API v1 - admin_user_management 路由注册失败: {e}")

    # 前端用户管理相关路由
    try:
        from .frontend_user_management import router as frontend_user_router
        router.include_router(frontend_user_router, prefix="/users", tags=["users"])
        logger.info("API v1 - frontend_user_management 路由已注册")
    except Exception as e:
        logger.error(f"API v1 - frontend_user_management 路由注册失败: {e}")

    # 简单用户API相关路由
    try:
        from .simple_user_api import router as simple_user_router
        router.include_router(simple_user_router, prefix="/users", tags=["users"])
        logger.info("API v1 - simple_user_api 路由已注册")
    except Exception as e:
        logger.error(f"API v1 - simple_user_api 路由注册失败: {e}")

    try:
        # 爬虫管理相关路由
        from .crawler import router as crawler_router
        router.include_router(crawler_router, prefix="/crawler", tags=["crawler"])
        logger.info("API v1 - crawler 路由已注册")
    except Exception as e:
        logger.error(f"API v1 - crawler 路由注册失败: {e}")

    # 返回router对象
    return router

# 创建并导出router对象
router = create_api_router()

__all__ = ["router"]