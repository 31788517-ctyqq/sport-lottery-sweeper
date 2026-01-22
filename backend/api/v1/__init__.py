"""
API v1 初始化
"""
from fastapi import APIRouter

# 导入所有API路由
from . import (
    lottery,  # 重命名自 jczq
    matches,
    public_matches,
    admin,
    auth,  # 认证API
    intelligence,
    data_submission
)

# 创建API v1路由器
router = APIRouter(prefix="/v1")

# 包含各个模块的路由
router.include_router(lottery.router)
router.include_router(matches.router)
router.include_router(public_matches.router)
router.include_router(admin.router)
router.include_router(auth.router)  # 包含认证路由
router.include_router(intelligence.router)
router.include_router(data_submission.router, prefix="/submission")  # 数据提交API使用/submission前缀

# 兼容旧路由 (deprecated, 保留3个月)
router.include_router(
    lottery.router,
    prefix="/jczq",
    tags=["[Deprecated] 竞彩足球 - Use /lottery instead"],
    deprecated=True
)

__all__ = ["router"]