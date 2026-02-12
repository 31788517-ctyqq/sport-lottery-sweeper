#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis缓存配置
"""

import redis
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    """Redis缓存管理器"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = False
        self._connect()
    
    def _connect(self):
        """连接Redis"""
        try:
            # 从环境变量获取Redis配置，如果没有则使用默认值
            import os
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", "6379"))
            redis_db = int(os.getenv("REDIS_DB", "0"))
            redis_password = os.getenv("REDIS_PASSWORD", None)
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # 测试连接
            self.redis_client.ping()
            self.enabled = True
            logger.info(f"Redis连接成功: {redis_host}:{redis_port}")
            
        except Exception as e:
            logger.warning(f"Redis连接失败，将使用内存缓存: {e}")
            self.enabled = False
            self.memory_cache = {}  # 简单的字典缓存作为备选
    
    def get(self, key: str) -> Optional[any]:
        """获取缓存值"""
        try:
            if self.enabled:
                value = self.redis_client.get(key)
                return json.loads(value) if value else None
            else:
                return self.memory_cache.get(key)
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return None
    
    def set(self, key: str, value: any, expire_seconds: int = 300):
        """设置缓存值"""
        try:
            serialized_value = json.dumps(value, ensure_ascii=False)
            
            if self.enabled:
                self.redis_client.setex(key, expire_seconds, serialized_value)
            else:
                self.memory_cache[key] = value
                # 简单的TTL管理（内存缓存不精确）
                if len(self.memory_cache) > 1000:  # 限制内存缓存大小
                    # 删除最旧的条目（简单实现）
                    oldest_key = next(iter(self.memory_cache))
                    del self.memory_cache[oldest_key]
                    
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
    
    def delete(self, key: str):
        """删除缓存"""
        try:
            if self.enabled:
                self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
    
    def clear_pattern(self, pattern: str):
        """清除匹配模式的所有缓存"""
        try:
            if self.enabled:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            else:
                # 内存缓存的简单模式匹配
                keys_to_delete = [k for k in self.memory_cache.keys() if pattern.replace("*", "") in k]
                for key in keys_to_delete:
                    del self.memory_cache[key]
        except Exception as e:
            logger.error(f"清除模式缓存失败: {e}")

# 全局缓存实例
cache = RedisCache()

# 缓存键前缀定义
CACHE_KEYS = {
    "BEIDAN_MATCHES": "beidan:matches:{date_time}",
    "BEIDAN_STRATEGIES": "beidan:strategies:{user_id}",
    "BEIDAN_STATS": "beidan:stats:{filters_hash}",
    "BEIDAN_LEAGUES": "beidan:leagues",
    "BEIDAN_DATETIME_OPTIONS": "beidan:datetime_options"
}