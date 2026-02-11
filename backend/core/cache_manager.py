"""
HybridCache - 混合缓存管理器
结合内存缓存和Redis缓存的高性能缓存系统
"""
import asyncio
import json
import logging
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


class HybridCache:
    """
    混合缓存系统，结合内存缓存和Redis缓存
    """
    
    def __init__(self, redis_url: Optional[str] = None, max_memory_items: int = 1000):
        self.redis_url = redis_url
        self.redis_client = None
        self.memory_cache: Dict[str, tuple] = {}  # key -> (value, expiration_time)
        self.max_memory_items = max_memory_items
        self.use_redis = bool(redis_url and REDIS_AVAILABLE)
        
    async def initialize(self):
        """初始化缓存系统"""
        if self.use_redis:
            try:
                self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
                # 测试Redis连接
                await self.redis_client.ping()
                logger.info("Redis缓存连接成功")
            except Exception as e:
                # 在开发环境中，Redis可能未安装，所以降低错误级别为info
                import os
                if os.getenv("ENVIRONMENT") == "production":
                    logger.error(f"Redis连接失败: {e}, 回退到内存缓存")
                else:
                    logger.info(f"Redis未运行({e})，回退到内存缓存 (开发环境中正常)")
                self.use_redis = False
                self.redis_client = None
        else:
            logger.info("使用内存缓存")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        """
        # 首先尝试从内存缓存获取
        if key in self.memory_cache:
            value, expires_at = self.memory_cache[key]
            if expires_at is None or expires_at > datetime.now():
                logger.debug(f"内存缓存命中: {key}")
                return value
            else:
                # 缓存已过期，从内存中删除
                del self.memory_cache[key]
        
        # 如果启用了Redis，尝试从Redis获取
        if self.use_redis and self.redis_client:
            try:
                cached_value = await self.redis_client.get(key)
                if cached_value:
                    try:
                        data = json.loads(cached_value)
                        value = data.get('value')
                        expires_at_str = data.get('expires_at')
                        
                        if expires_at_str:
                            expires_at = datetime.fromisoformat(expires_at_str)
                            if expires_at <= datetime.now():
                                # Redis中的缓存已过期
                                await self.delete(key)
                                return None
                        
                        # 更新内存缓存
                        self._add_to_memory_cache(key, value, expires_at)
                        logger.debug(f"Redis缓存命中: {key}")
                        return value
                    except json.JSONDecodeError:
                        # 如果不是JSON格式，直接返回
                        return cached_value
            except Exception as e:
                logger.error(f"Redis获取缓存失败: {e}")
        
        logger.debug(f"缓存未命中: {key}")
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存值
        :param key: 缓存键
        :param value: 缓存值
        :param ttl: 过期时间（秒）
        :return: 是否设置成功
        """
        # 计算过期时间
        expires_at = None
        if ttl:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        
        # 添加到内存缓存
        self._add_to_memory_cache(key, value, expires_at)
        
        # 如果启用了Redis，也添加到Redis
        if self.use_redis and self.redis_client:
            try:
                data = {
                    'value': value,
                    'expires_at': expires_at.isoformat() if expires_at else None,
                    'set_at': datetime.now().isoformat()
                }
                if ttl:
                    await self.redis_client.setex(key, ttl, json.dumps(data))
                else:
                    await self.redis_client.set(key, json.dumps(data))
            except Exception as e:
                logger.error(f"Redis设置缓存失败: {e}")
                return False
        
        logger.debug(f"缓存设置成功: {key}, TTL: {ttl}")
        return True
    
    def _add_to_memory_cache(self, key: str, value: Any, expires_at: Optional[datetime]):
        """添加到内存缓存"""
        # 检查是否超过最大容量，如果是则删除最旧的条目
        if len(self.memory_cache) >= self.max_memory_items:
            # 删除最早的一个项目
            oldest_key = next(iter(self.memory_cache))
            del self.memory_cache[oldest_key]
        
        self.memory_cache[key] = (value, expires_at)
    
    async def delete(self, key: str) -> bool:
        """
        删除缓存键
        """
        # 从内存缓存删除
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # 从Redis删除
        if self.use_redis and self.redis_client:
            try:
                await self.redis_client.delete(key)
                return True
            except Exception as e:
                logger.error(f"Redis删除缓存失败: {e}")
                return False
        
        return True
    
    async def clear(self) -> bool:
        """
        清空所有缓存
        """
        self.memory_cache.clear()
        
        if self.use_redis and self.redis_client:
            try:
                await self.redis_client.flushdb()
                return True
            except Exception as e:
                logger.error(f"Redis清空缓存失败: {e}")
                return False
        
        return True
    
    async def close(self):
        """
        关闭缓存连接
        """
        if self.redis_client:
            await self.redis_client.close()
            await self.redis_client.connection_pool.disconnect()
    
    async def get_keys(self, pattern: str = "*") -> list:
        """
        获取匹配模式的所有键
        """
        keys = []
        
        # 从内存缓存获取匹配的键
        for key in self.memory_cache:
            if self._match_pattern(key, pattern):
                keys.append(key)
        
        # 从Redis获取匹配的键
        if self.use_redis and self.redis_client:
            try:
                redis_keys = await self.redis_client.keys(pattern)
                keys.extend(redis_keys)
            except Exception as e:
                logger.error(f"Redis获取键失败: {e}")
        
        return list(set(keys))  # 去重
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """
        简单的模式匹配
        """
        if pattern == "*":
            return True
        
        # 支持简单的通配符模式
        import fnmatch
        return fnmatch.fnmatch(key, pattern)


def get_cache_manager():
    """
    获取缓存管理器实例
    """
    from .config import get_settings
    settings = get_settings()
    cache = HybridCache(
        redis_url=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
    )
    return cache


# 示例使用
async def demo():
    cache = HybridCache(redis_url="redis://localhost:6379/0")
    await cache.initialize()
    
    # 设置一个值
    await cache.set("test_key", {"data": "example"}, ttl=60)
    
    # 获取值
    value = await cache.get("test_key")
    print(value)  # {'data': 'example'}
    
    await cache.close()


if __name__ == "__main__":
    asyncio.run(demo())