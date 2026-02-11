"""
缓存依赖模块
提供全局缓存实例供API端点使用
"""
from typing import Optional
import logging
from fastapi import Depends

from backend.core.config import get_settings
from ...app.cache.cache_manager import HybridCache, init_cache

logger = logging.getLogger(__name__)

# 全局缓存实例
_cache_instance: Optional[HybridCache] = None


async def get_cache() -> HybridCache:
    """
    获取缓存实例的依赖函数
    """
    global _cache_instance
    if _cache_instance is None:
        settings = get_settings()
        redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        if settings.REDIS_PASSWORD:
            redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        
        _cache_instance = HybridCache(redis_url)
        await _cache_instance.initialize()
        logger.info("缓存系统已初始化")
    
    return _cache_instance


async def cache_dependency():
    """
    缓存依赖项，供FastAPI依赖注入使用
    """
    cache = await get_cache()
    return cache
