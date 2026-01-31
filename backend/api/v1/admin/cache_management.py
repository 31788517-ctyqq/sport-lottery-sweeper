"""
缓存管理API端点
提供缓存操作和统计功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import json
import time

from backend.database import get_db
from backend.core.auth import get_current_admin_user
from backend.models.user import User
from backend.core.cache_manager import HybridCache
from backend.core.config import get_settings

router = APIRouter()

# 初始化缓存实例
settings = get_settings()
cache = HybridCache(
    redis_url=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
)

@router.on_event("startup")
async def startup_event():
    await cache.initialize()

@router.get("/cache/stats")
async def get_cache_stats():
    """获取缓存统计信息"""
    try:
        # 获取缓存中的键数量
        keys = await cache.get_keys("*")
        stats = {
            "total_keys": len(keys),
            "status": "connected" if cache.redis_client or len(cache.memory_cache) > 0 else "disconnected",
            "memory_cached_items": len(cache.memory_cache),
            "timestamp": time.time()
        }
        return {"code": 200, "message": "success", "data": stats}
    except Exception as e:
        return {"code": 500, "message": str(e), "data": {}}


@router.get("/cache/keys")
async def get_cache_keys(pattern: str = Query(default="*", description="键名模式")):
    """获取匹配模式的缓存键列表"""
    try:
        keys = await cache.get_keys(pattern)
        return {"code": 200, "message": "success", "data": {"keys": keys, "total": len(keys)}}
    except Exception as e:
        return {"code": 500, "message": str(e), "data": {}}


@router.post("/cache/clear")
async def clear_cache():
    """清空所有缓存"""
    try:
        success = await cache.clear()
        if success:
            return {"code": 200, "message": "缓存已清空", "data": {}}
        else:
            return {"code": 500, "message": "清空缓存失败", "data": {}}
    except Exception as e:
        return {"code": 500, "message": str(e), "data": {}}


@router.get("/cache/key/{key}")
async def get_cache_value(key: str):
    """获取指定键的缓存值"""
    try:
        value = await cache.get(key)
        if value is not None:
            return {"code": 200, "message": "success", "data": {"key": key, "value": value}}
        else:
            return {"code": 404, "message": "键不存在", "data": {}}
    except Exception as e:
        return {"code": 500, "message": str(e), "data": {}}


@router.delete("/cache/key/{key}")
async def delete_cache_key(key: str):
    """删除指定键的缓存"""
    try:
        success = await cache.delete(key)
        if success:
            return {"code": 200, "message": f"缓存键 '{key}' 已删除", "data": {}}
        else:
            return {"code": 500, "message": f"删除缓存键 '{key}' 失败", "data": {}}
    except Exception as e:
        return {"code": 500, "message": str(e), "data": {}}


@router.post("/cache/key/{key}")
async def set_cache_value(key: str, value: Dict[str, Any]):
    """设置缓存值"""
    try:
        ttl = value.get("ttl", 3600)  # 默认TTL为1小时
        cache_value = {k: v for k, v in value.items() if k != "ttl"}  # 除去ttl字段
        
        success = await cache.set(key, cache_value, ttl)
        if success:
            return {"code": 200, "message": f"缓存键 '{key}' 已设置", "data": {}}
        else:
            return {"code": 500, "message": f"设置缓存键 '{key}' 失败", "data": {}}
    except Exception as e:
        return {"code": 500, "message": str(e), "data": {}}
