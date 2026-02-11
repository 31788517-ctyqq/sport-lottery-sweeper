"""
缓存策略优化器
优化缓存策略，提高系统性能
"""
import logging
import time
import json
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)


class CacheStrategyOptimizer:
    """缓存策略优化器"""
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }
        self.strategies = {
            "ttl_based": self._ttl_based_strategy,
            "lru": self._lru_strategy,
            "lfu": self._lfu_strategy,
            "adaptive": self._adaptive_strategy
        }
        
    async def get_with_optimized_strategy(
        self, 
        key: str, 
        strategy: str = "adaptive",
        fallback_func: Optional[Callable] = None,
        fallback_args: tuple = (),
        fallback_kwargs: Optional[Dict] = None,
        ttl: Optional[int] = None
    ) -> Any:
        """
        使用优化策略获取缓存值
        
        Args:
            key: 缓存键
            strategy: 缓存策略 (ttl_based, lru, lfu, adaptive)
            fallback_func: 缓存未命中时的回退函数
            fallback_args: 回退函数参数
            fallback_kwargs: 回退函数关键字参数
            ttl: 缓存过期时间（秒）
            
        Returns:
            缓存值或回退函数结果
        """
        self.cache_stats["total_requests"] += 1
        
        # 尝试从缓存获取
        cached_value = await self.cache_manager.get(key)
        
        if cached_value is not None:
            self.cache_stats["hits"] += 1
            logger.debug(f"缓存命中: {key}")
            return cached_value
        
        self.cache_stats["misses"] += 1
        logger.debug(f"缓存未命中: {key}")
        
        # 缓存未命中，执行回退函数
        if fallback_func is not None:
            try:
                # 执行回退函数获取数据
                if asyncio.iscoroutinefunction(fallback_func):
                    result = await fallback_func(*fallback_args, **(fallback_kwargs or {}))
                else:
                    result = fallback_func(*fallback_args, **(fallback_kwargs or {}))
                
                # 根据策略决定是否缓存结果
                should_cache = await self._apply_strategy(strategy, key, result)
                
                if should_cache and ttl:
                    await self.cache_manager.set(key, result, ttl=ttl)
                    logger.debug(f"已缓存结果: {key}, TTL: {ttl}秒")
                
                return result
                
            except Exception as e:
                logger.error(f"回退函数执行失败: {key} - 错误: {e}")
                raise
        
        return None
    
    async def _apply_strategy(self, strategy: str, key: str, value: Any) -> bool:
        """
        应用缓存策略
        
        Args:
            strategy: 缓存策略
            key: 缓存键
            value: 缓存值
            
        Returns:
            是否应该缓存
        """
        strategy_func = self.strategies.get(strategy, self._adaptive_strategy)
        return await strategy_func(key, value)
    
    async def _ttl_based_strategy(self, key: str, value: Any) -> bool:
        """TTL基础策略：总是缓存"""
        return True
    
    async def _lru_strategy(self, key: str, value: Any) -> bool:
        """LRU策略：最近最少使用"""
        # 这里可以添加LRU逻辑
        # 例如：检查缓存大小，如果超过限制则淘汰最久未使用的
        return True
    
    async def _lfu_strategy(self, key: str, value: Any) -> bool:
        """LFU策略：最不经常使用"""
        # 这里可以添加LFU逻辑
        return True
    
    async def _adaptive_strategy(self, key: str, value: Any) -> bool:
        """自适应策略：根据访问模式动态调整"""
        # 基于以下因素决定是否缓存：
        # 1. 数据大小
        # 2. 访问频率
        # 3. 数据重要性
        # 4. 计算成本
        
        try:
            # 检查数据大小
            data_size = len(str(value))
            
            # 小数据优先缓存
            if data_size < 1024 * 10:  # 小于10KB
                return True
            
            # 大数据根据访问频率决定
            # 这里可以添加访问频率统计逻辑
            
            return True
            
        except:
            return True
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total = self.cache_stats["total_requests"]
        hit_rate = (self.cache_stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            **self.cache_stats,
            "hit_rate": f"{hit_rate:.2f}%",
            "miss_rate": f"{100 - hit_rate:.2f}%",
            "timestamp": datetime.now().isoformat()
        }
    
    def reset_stats(self):
        """重置统计信息"""
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }


class MultiLevelCache:
    """多级缓存系统"""
    
    def __init__(self):
        self.level1_cache = {}  # 内存缓存
        self.level2_cache = None  # Redis缓存
        self.level3_cache = None  # 分布式缓存
        
        self.level1_ttl = 60  # 1分钟
        self.level2_ttl = 300  # 5分钟
        self.level3_ttl = 3600  # 1小时
        
        self.access_patterns = {}
        
    async def get(self, key: str) -> Optional[Any]:
        """从多级缓存获取值"""
        # 第一级：内存缓存
        if key in self.level1_cache:
            value, timestamp = self.level1_cache[key]
            if time.time() - timestamp < self.level1_ttl:
                self._record_access(key, "level1")
                return value
            else:
                del self.level1_cache[key]
        
        # 第二级：Redis缓存
        if self.level2_cache:
            try:
                value = await self.level2_cache.get(key)
                if value is not None:
                    # 更新到第一级缓存
                    self.level1_cache[key] = (value, time.time())
                    self._record_access(key, "level2")
                    return value
            except Exception as e:
                logger.error(f"Redis缓存获取失败: {key} - 错误: {e}")
        
        # 第三级：分布式缓存
        if self.level3_cache:
            try:
                value = await self.level3_cache.get(key)
                if value is not None:
                    # 更新到第一级和第二级缓存
                    self.level1_cache[key] = (value, time.time())
                    if self.level2_cache:
                        await self.level2_cache.set(key, value, ttl=self.level2_ttl)
                    self._record_access(key, "level3")
                    return value
            except Exception as e:
                logger.error(f"分布式缓存获取失败: {key} - 错误: {e}")
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置多级缓存值"""
        # 设置第一级缓存
        cache_ttl = ttl or self.level1_ttl
        self.level1_cache[key] = (value, time.time())
        
        # 设置第二级缓存
        if self.level2_cache and cache_ttl > self.level1_ttl:
            try:
                await self.level2_cache.set(key, value, ttl=min(cache_ttl, self.level2_ttl))
            except Exception as e:
                logger.error(f"Redis缓存设置失败: {key} - 错误: {e}")
        
        # 设置第三级缓存
        if self.level3_cache and cache_ttl > self.level2_ttl:
            try:
                await self.level3_cache.set(key, value, ttl=min(cache_ttl, self.level3_ttl))
            except Exception as e:
                logger.error(f"分布式缓存设置失败: {key} - 错误: {e}")
    
    def _record_access(self, key: str, level: str):
        """记录缓存访问模式"""
        if key not in self.access_patterns:
            self.access_patterns[key] = {
                "access_count": 0,
                "last_access": datetime.now(),
                "access_levels": []
            }
        
        self.access_patterns[key]["access_count"] += 1
        self.access_patterns[key]["last_access"] = datetime.now()
        self.access_patterns[key]["access_levels"].append({
            "level": level,
            "timestamp": datetime.now().isoformat()
        })
        
        # 限制记录数量
        if len(self.access_patterns) > 1000:
            # 删除最久未访问的记录
            oldest_key = min(
                self.access_patterns.keys(),
                key=lambda k: self.access_patterns[k]["last_access"]
            )
            del self.access_patterns[oldest_key]
    
    def get_access_patterns(self) -> Dict[str, Any]:
        """获取访问模式分析"""
        return {
            "total_keys": len(self.access_patterns),
            "patterns": self.access_patterns,
            "analysis": self._analyze_access_patterns()
        }
    
    def _analyze_access_patterns(self) -> Dict[str, Any]:
        """分析访问模式"""
        if not self.access_patterns:
            return {}
        
        total_accesses = sum(
            info["access_count"] for info in self.access_patterns.values()
        )
        
        # 计算访问频率分布
        access_counts = [info["access_count"] for info in self.access_patterns.values()]
        
        return {
            "total_accesses": total_accesses,
            "average_access_per_key": total_accesses / len(self.access_patterns),
            "max_access_count": max(access_counts) if access_counts else 0,
            "min_access_count": min(access_counts) if access_counts else 0,
            "hot_keys": self._get_hot_keys(10)
        }
    
    def _get_hot_keys(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """获取热点键"""
        sorted_keys = sorted(
            self.access_patterns.items(),
            key=lambda x: x[1]["access_count"],
            reverse=True
        )[:top_n]
        
        return [
            {
                "key": key,
                "access_count": info["access_count"],
                "last_access": info["last_access"].isoformat()
            }
            for key, info in sorted_keys
        ]


def cache_with_strategy(
    strategy: str = "adaptive",
    ttl: int = 300,
    key_prefix: str = "cache"
):
    """
    缓存策略装饰器
    
    Args:
        strategy: 缓存策略
        ttl: 缓存过期时间（秒）
        key_prefix: 缓存键前缀
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 这里需要实际的缓存管理器实例
            # 为了示例，我们假设有一个全局缓存管理器
            from backend.core.cache_manager import get_cache_manager
            
            cache_manager = await get_cache_manager()
            optimizer = CacheStrategyOptimizer(cache_manager)
            
            # 定义回退函数
            async def fallback():
                return await func(*args, **kwargs)
            
            # 使用优化策略获取缓存
            result = await optimizer.get_with_optimized_strategy(
                key=cache_key,
                strategy=strategy,
                fallback_func=fallback,
                ttl=ttl
            )
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 同步函数版本
            import asyncio
            
            async def async_func():
                return await async_wrapper(*args, **kwargs)
            
            return asyncio.run(async_func())
        
        # 根据函数类型返回相应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class CachePreheater:
    """缓存预热器"""
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.preheat_configs = {}
        
    def register_preheat_config(self, name: str, config: Dict[str, Any]):
        """注册预热配置"""
        self.preheat_configs[name] = config
    
    async def preheat_cache(self, config_name: str):
        """预热缓存"""
        config = self.preheat_configs.get(config_name)
        if not config:
            logger.warning(f"预热配置不存在: {config_name}")
            return
        
        logger.info(f"开始预热缓存: {config_name}")
        
        try:
            # 执行预热任务
            tasks = config.get("tasks", [])
            for task in tasks:
                await self._execute_preheat_task(task)
                
            logger.info(f"缓存预热完成: {config_name}")
            
        except Exception as e:
            logger.error(f"缓存预热失败: {config_name} - 错误: {e}")
    
    async def _execute_preheat_task(self, task: Dict[str, Any]):
        """执行预热任务"""
        task_type = task.get("type")
        
        if task_type == "data_query":
            await self._preheat_data_query(task)
        elif task_type == "api_call":
            await self._preheat_api_call(task)
        elif task_type == "static_data":
            await self._preheat_static_data(task)
        else:
            logger.warning(f"未知的预热任务类型: {task_type}")
    
    async def _preheat_data_query(self, task: Dict[str, Any]):
        """预热数据查询"""
        # 这里需要根据具体的数据查询逻辑实现
        pass
    
    async def _preheat_api_call(self, task: Dict[str, Any]):
        """预热API调用"""
        # 这里需要根据具体的API调用逻辑实现
        pass
    
    async def _preheat_static_data(self, task: Dict[str, Any]):
        """预热静态数据"""
        key = task.get("key")
        value = task.get("value")
        ttl = task.get("ttl", 3600)
        
        if key and value is not None:
            await self.cache_manager.set(key, value, ttl=ttl)
            logger.debug(f"已预热静态数据: {key}")


# 缓存策略配置
CACHE_STRATEGY_CONFIGS = {
    "high_frequency": {
        "strategy": "adaptive",
        "ttl": 60,  # 1分钟
        "description": "高频访问数据，短TTL"
    },
    "low_frequency": {
        "strategy": "ttl_based",
        "ttl": 3600,  # 1小时
        "description": "低频访问数据，长TTL"
    },
    "critical_data": {
        "strategy": "lru",
        "ttl": 300,  # 5分钟
        "description": "关键数据，LRU策略"
    },
    "large_data": {
        "strategy": "lfu",
        "ttl": 1800,  # 30分钟
        "description": "大数据，LFU策略"
    }
}


# 示例使用
if __name__ == "__main__":
    print("缓存策略优化器初始化完成")
    print("可用缓存策略:", list(CACHE_STRATEGY_CONFIGS.keys()))
    
    # 示例：创建多级缓存系统
    ml_cache = MultiLevelCache()
    print("多级缓存系统已创建")