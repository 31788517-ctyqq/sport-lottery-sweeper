"""
查询优化集成模块
将数据库查询优化和缓存策略集成到现有系统中
"""
import logging
from typing import Dict, Any, Optional, List
from functools import wraps
from datetime import datetime, timedelta
import asyncio

from sqlalchemy.orm import Session, Query
from sqlalchemy import event

from .database_query_optimizer import DatabaseQueryOptimizer, query_performance_monitor, QueryCacheManager
from .cache_strategy_optimizer import CacheStrategyOptimizer, cache_with_strategy, MultiLevelCache
from ..core.cache_manager import get_cache_manager

logger = logging.getLogger(__name__)


class QueryOptimizationIntegration:
    """查询优化集成类"""
    
    def __init__(self):
        self.query_optimizer = None
        self.cache_strategy_optimizer = None
        self.multi_level_cache = None
        self.query_cache_manager = QueryCacheManager()
        self.optimization_enabled = True
        
        # 性能统计
        self.stats = {
            'query_optimizations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'slow_queries': 0,
            'total_query_time': 0.0
        }
    
    def initialize(self, db_session: Session):
        """初始化优化器"""
        if not self.optimization_enabled:
            return
        
        # 初始化查询优化器
        self.query_optimizer = DatabaseQueryOptimizer(db_session)
        
        # 初始化缓存策略优化器
        cache_manager = get_cache_manager()
        self.cache_strategy_optimizer = CacheStrategyOptimizer(cache_manager)
        
        # 初始化多级缓存
        self.multi_level_cache = MultiLevelCache()
        
        logger.info("查询优化集成初始化完成")
    
    def optimize_query(self, query: Query, use_cache: bool = True) -> Query:
        """优化查询"""
        if not self.optimization_enabled or not self.query_optimizer:
            return query
        
        try:
            optimized_query = self.query_optimizer.optimize_query(query, use_cache)
            self.stats['query_optimizations'] += 1
            return optimized_query
        except Exception as e:
            logger.warning(f"查询优化失败: {e}")
            return query
    
    async def get_with_cache(self, cache_key: str, query_func, 
                           strategy: str = "adaptive", ttl: int = 300, 
                           *args, **kwargs) -> Any:
        """使用缓存获取数据"""
        if not self.optimization_enabled or not self.cache_strategy_optimizer:
            # 直接执行查询函数
            return await query_func(*args, **kwargs) if asyncio.iscoroutinefunction(query_func) else query_func(*args, **kwargs)
        
        try:
            result = await self.cache_strategy_optimizer.get_with_optimized_strategy(
                key=cache_key,
                strategy=strategy,
                fallback_func=query_func,
                fallback_args=args,
                fallback_kwargs=kwargs,
                ttl=ttl
            )
            
            # 更新统计
            if result is not None:
                self.stats['cache_hits'] += 1
            else:
                self.stats['cache_misses'] += 1
                
            return result
        except Exception as e:
            logger.warning(f"缓存策略执行失败: {e}")
            # 回退到直接查询
            return await query_func(*args, **kwargs) if asyncio.iscoroutinefunction(query_func) else query_func(*args, **kwargs)
    
    def execute_query_with_monitoring(self, query: Query, description: str = "") -> List[Any]:
        """执行查询并监控性能"""
        if not self.optimization_enabled or not self.query_optimizer:
            return query.all()
        
        try:
            result = self.query_optimizer.execute_with_monitoring(query, description)
            
            # 记录查询时间（简化处理）
            # 在实际应用中，应该从监控装饰器中获取执行时间
            self.stats['total_query_time'] += 0.1  # 占位值
            
            return result
        except Exception as e:
            logger.warning(f"查询监控执行失败: {e}")
            return query.all()
    
    def analyze_table_indexes(self, table_name: str) -> Dict[str, Any]:
        """分析表索引"""
        if not self.optimization_enabled or not self.query_optimizer:
            return {"error": "优化器未初始化"}
        
        try:
            return self.query_optimizer.analyze_table_indexes(table_name)
        except Exception as e:
            logger.error(f"表索引分析失败: {e}")
            return {"error": str(e)}
    
    def create_recommended_indexes(self, recommendations: List[Dict[str, Any]]):
        """创建推荐的索引"""
        if not self.optimization_enabled or not self.query_optimizer:
            return
        
        try:
            self.query_optimizer.create_recommended_indexes(recommendations)
        except Exception as e:
            logger.error(f"创建索引失败: {e}")
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """获取优化统计信息"""
        total_queries = self.stats['cache_hits'] + self.stats['cache_misses']
        cache_hit_rate = self.stats['cache_hits'] / total_queries if total_queries > 0 else 0
        
        return {
            **self.stats,
            'cache_hit_rate': f"{cache_hit_rate:.2%}",
            'optimization_enabled': self.optimization_enabled,
            'timestamp': datetime.now().isoformat()
        }
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'query_optimizations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'slow_queries': 0,
            'total_query_time': 0.0
        }
    
    def enable_optimization(self, enabled: bool = True):
        """启用或禁用优化"""
        self.optimization_enabled = enabled
        logger.info(f"查询优化已{'启用' if enabled else '禁用'}")


# 全局优化集成实例
_query_optimization_integration = None


def get_query_optimization_integration() -> QueryOptimizationIntegration:
    """获取查询优化集成实例"""
    global _query_optimization_integration
    if _query_optimization_integration is None:
        _query_optimization_integration = QueryOptimizationIntegration()
    return _query_optimization_integration


# 装饰器：优化数据库查询
def optimize_database_query(use_cache: bool = True, cache_key_prefix: str = "query"):
    """优化数据库查询装饰器"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 获取优化集成实例
            optimization = get_query_optimization_integration()
            
            # 生成缓存键
            cache_key = f"{cache_key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 定义查询函数
            async def execute_query():
                # 执行原始函数
                result = await func(*args, **kwargs)
                return result
            
            # 使用缓存获取结果
            if use_cache and optimization.optimization_enabled:
                result = await optimization.get_with_cache(
                    cache_key=cache_key,
                    query_func=execute_query,
                    strategy="adaptive",
                    ttl=300  # 5分钟
                )
            else:
                result = await execute_query()
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 同步版本
            import asyncio
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        # 根据函数类型返回相应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# 装饰器：监控查询性能
def monitor_query_performance(description: str = ""):
    """监控查询性能装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 应用性能监控
            monitored_func = query_performance_monitor(func)
            return monitored_func(*args, **kwargs)
        
        return wrapper
    
    return decorator


# 数据库事件监听器
def setup_database_event_listeners():
    """设置数据库事件监听器"""
    
    @event.listens_for(Session, 'before_execute')
    def before_execute(conn, clauseelement, multiparams, params, execution_options):
        """执行前监听"""
        logger.debug(f"准备执行SQL: {clauseelement}")
    
    @event.listens_for(Session, 'after_execute')
    def after_execute(conn, clauseelement, multiparams, params, execution_options, result):
        """执行后监听"""
        logger.debug(f"SQL执行完成: {clauseelement}")


# 常用查询优化模式集成
def apply_common_optimization_patterns(query: Query, pattern: str = "limit_offset") -> Query:
    """应用常用查询优化模式"""
    from .database_query_optimizer import COMMON_OPTIMIZATION_PATTERNS
    
    if pattern not in COMMON_OPTIMIZATION_PATTERNS:
        logger.warning(f"未知的优化模式: {pattern}")
        return query
    
    pattern_info = COMMON_OPTIMIZATION_PATTERNS[pattern]
    logger.info(f"应用优化模式: {pattern_info['description']}")
    logger.info(f"建议: {pattern_info['suggestion']}")
    
    # 这里可以根据具体模式应用优化
    # 例如，对于limit_offset模式，可以尝试转换为游标分页
    
    return query


# 缓存预热功能
async def preheat_common_queries(db_session: Session):
    """预热常用查询缓存"""
    optimization = get_query_optimization_integration()
    
    if not optimization.optimization_enabled:
        return
    
    logger.info("开始预热常用查询缓存")
    
    # 预热配置
    preheat_configs = [
        {
            'key': 'cache:preheat:active_sources',
            'query': "SELECT COUNT(*) FROM data_sources WHERE status = true",
            'ttl': 600  # 10分钟
        },
        {
            'key': 'cache:preheat:recent_matches',
            'query': "SELECT * FROM matches WHERE match_time > datetime('now', '-7 days') ORDER BY match_time DESC LIMIT 50",
            'ttl': 300  # 5分钟
        },
        {
            'key': 'cache:preheat:top_leagues',
            'query': "SELECT league_id, COUNT(*) as match_count FROM matches GROUP BY league_id ORDER BY match_count DESC LIMIT 10",
            'ttl': 1800  # 30分钟
        }
    ]
    
    for config in preheat_configs:
        try:
            # 执行查询并缓存结果
            result = db_session.execute(config['query']).fetchall()
            
            # 缓存结果
            await optimization.cache_strategy_optimizer.get_with_optimized_strategy(
                key=config['key'],
                strategy="ttl_based",
                fallback_func=lambda: result,
                ttl=config['ttl']
            )
            
            logger.debug(f"已预热缓存: {config['key']}")
            
        except Exception as e:
            logger.warning(f"预热缓存失败 {config['key']}: {e}")
    
    logger.info("常用查询缓存预热完成")


# 示例使用
if __name__ == "__main__":
    print("查询优化集成模块初始化完成")
    print("功能包括:")
    print("1. 数据库查询优化")
    print("2. 缓存策略优化")
    print("3. 查询性能监控")
    print("4. 常用查询缓存预热")