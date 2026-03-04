"""
管理后台初始化模块
"""
from fastapi import APIRouter
from .api.v1 import router as admin_v1_router


def create_admin_router():
    """创建管理后台路由器"""
    router = APIRouter(prefix="/admin", tags=["admin"])
    
    # 包含管理后台API路由
    router.include_router(admin_v1_router, prefix="/v1")
    
    return router


# 管理后台路由器实例
admin_router = create_admin_router()

__all__ = ["admin_router"]