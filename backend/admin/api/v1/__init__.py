"""
管理后台API v1初始化
"""
from fastapi import APIRouter
from . import (
    user_admin,
    data_admin,
    system_admin,
    match_admin,
    review_admin,
    crawler_config_admin,
    intelligence_admin,
    menu_admin
)

# 创建管理后台API v1路由器
router = APIRouter(prefix="/admin/v1", tags=["admin-v1"])

# 包含各个管理模块的路由
router.include_router(user_admin.router)
router.include_router(data_admin.router)
router.include_router(system_admin.router)
router.include_router(match_admin.router)
router.include_router(review_admin.router)
router.include_router(crawler_config_admin.router)
router.include_router(intelligence_admin.router)
router.include_router(menu_admin.router)

__all__ = ["router"]