"""
高级缓存管理器
实现多级缓存策略，优化数据访问性能
"""
import asyncio
import json
import pickle
from typing import Any, Optional, Dict, Tuple
from datetime import datetime, timedelta
import logging
import hashlib


class AdvancedCacheManager:
    """
    高级缓存管理器
    实现内存缓存和持久化缓存的多级缓存策略
    """
    def __init__(self):
        self._memory_cache: Dict[str, Tuple[Any, datetime]] = {}
        self._default_ttl = timedelta(minutes=10)
        self.logger = logging.getLogger(__name__)

    def _generate_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_str = f"{args}_{sorted(kwargs.items())}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _is_expired(self, timestamp: datetime, ttl: timedelta) -> bool:
        """检查缓存是否过期"""
        return datetime.now() > timestamp + ttl

    async def get(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        if key in self._memory_cache:
            data, timestamp = self._memory_cache[key]
            # 这里假设默认TTL，实际使用中可以从键中提取TTL信息
            if not self._is_expired(timestamp, self._default_ttl):
                self.logger.debug(f"内存缓存命中: {key}")
                return data
            else:
                # 删除过期缓存
                del self._memory_cache[key]
                self.logger.debug(f"内存缓存过期: {key}")
        
        return None

    async def set(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> None:
        """设置缓存数据"""
        if ttl is None:
            ttl = self._default_ttl
        
        self._memory_cache[key] = (value, datetime.now() + ttl - self._default_ttl)
        self.logger.debug(f"设置缓存: {key}, TTL: {ttl}")

    async def invalidate(self, key: str) -> None:
        """使缓存失效"""
        if key in self._memory_cache:
            del self._memory_cache[key]
            self.logger.debug(f"缓存失效: {key}")

    async def invalidate_pattern(self, pattern: str) -> int:
        """按模式使缓存失效"""
        import re
        count = 0
        pattern_re = re.compile(pattern.replace("*", ".*"))
        
        keys_to_remove = []
        for key in self._memory_cache.keys():
            if pattern_re.match(key):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self._memory_cache[key]
            count += 1
        
        self.logger.debug(f"按模式失效缓存: {pattern}, 删除 {count} 个项目")
        return count

    async def clear(self) -> None:
        """清除所有缓存"""
        self._memory_cache.clear()
        self.logger.debug("清除所有缓存")

    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        active_items = 0
        expired_items = 0
        
        for key, (data, timestamp) in self._memory_cache.items():
            if self._is_expired(timestamp, self._default_ttl):
                expired_items += 1
            else:
                active_items += 1
        
        return {
            "total_items": len(self._memory_cache),
            "active_items": active_items,
            "expired_items": expired_items,
            "hit_rate": "N/A"  # 在实际实现中需要跟踪命中率
        }


class LazyLoader:
    """
    懒加载装饰器
    只有在实际访问时才加载数据
    """
    def __init__(self, loader_func, *args, **kwargs):
        self.loader_func = loader_func
        self.args = args
        self.kwargs = kwargs
        self._loaded = False
        self._value = None

    async def _load(self):
        """异步加载数据"""
        if not self._loaded:
            self._value = await self.loader_func(*self.args, **self.kwargs)
            self._loaded = True
        return self._value

    def __await__(self):
        return self._load().__await__()

    async def get(self):
        """获取加载的值"""
        return await self._load()


def cached_method(ttl_seconds: int = 600):
    """
    方法缓存装饰器
    自动缓存方法的返回值
    """
    def decorator(func):
        cache_key_prefix = f"{func.__module__}.{func.__qualname__}"

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成基于参数的缓存键
            cache_manager = AdvancedCacheManager()
            cache_key = f"{cache_key_prefix}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # 尝试从缓存获取
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行原方法
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # 存储到缓存
            await cache_manager.set(cache_key, result, timedelta(seconds=ttl_seconds))
            
            return result
        
        return wrapper
    return decorator


# 创建全局缓存管理器实例
_cache_manager = AdvancedCacheManager()


def get_cache_manager() -> AdvancedCacheManager:
    """获取缓存管理器实例"""
    return _cache_manager