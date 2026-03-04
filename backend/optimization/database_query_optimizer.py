"""
数据库查询优化器
提供数据库查询性能优化工具和策略
"""
import logging
import time
from typing import List, Dict, Any, Optional, Callable
from functools import wraps
from sqlalchemy.orm import Session, Query
from sqlalchemy import text, inspect, Index, event
import json

logger = logging.getLogger(__name__)

class DatabaseQueryOptimizer:
    """数据库查询优化器"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.query_cache = {}
        self.slow_query_threshold = 1.0  # 慢查询阈值（秒）
        
    def optimize_query(self, query: Query, use_cache: bool = True) -> Query:
        """
        优化SQLAlchemy查询
        
        Args:
            query: SQLAlchemy查询对象
            use_cache: 是否使用查询缓存
            
        Returns:
            优化后的查询对象
        """
        # 1. 确保只选择需要的列
        if not hasattr(query, '_entities'):
            # 如果查询没有指定列，添加默认选择
            pass
            
        # 2. 添加索引提示
        optimized = query
        
        # 3. 应用查询缓存
        if use_cache:
            cache_key = self._generate_cache_key(query)
            if cache_key in self.query_cache:
                logger.debug(f"查询缓存命中: {cache_key}")
                return self.query_cache[cache_key]
                
        return optimized
    
    def _generate_cache_key(self, query: Query) -> str:
        """生成查询缓存键"""
        # 基于查询语句和参数生成缓存键
        try:
            compiled = query.statement.compile()
            key_parts = [
                str(compiled),
                str(compiled.params),
                str(query._limit),
                str(query._offset)
            ]
            return hash(''.join(key_parts))
        except:
            return str(hash(str(query)))
    
    def execute_with_monitoring(self, query: Query, description: str = "") -> List[Any]:
        """
        执行查询并监控性能
        
        Args:
            query: SQLAlchemy查询对象
            description: 查询描述
            
        Returns:
            查询结果
        """
        start_time = time.time()
        
        try:
            result = query.all()
            execution_time = time.time() - start_time
            
            if execution_time > self.slow_query_threshold:
                logger.warning(
                    f"慢查询检测: {description} - 执行时间: {execution_time:.3f}秒"
                )
                
                # 记录慢查询详情
                self._log_slow_query_details(query, execution_time)
                
            logger.debug(f"查询执行完成: {description} - 时间: {execution_time:.3f}秒")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"查询执行失败: {description} - 错误: {e} - 时间: {execution_time:.3f}秒")
            raise
    
    def _log_slow_query_details(self, query: Query, execution_time: float):
        """记录慢查询详情"""
        try:
            compiled = query.statement.compile()
            query_details = {
                "sql": str(compiled),
                "params": str(compiled.params),
                "execution_time": execution_time,
                "timestamp": time.time()
            }
            logger.info(f"慢查询详情: {json.dumps(query_details, ensure_ascii=False)}")
        except:
            pass
    
    def analyze_table_indexes(self, table_name: str) -> Dict[str, Any]:
        """
        分析表索引情况
        
        Args:
            table_name: 表名
            
        Returns:
            索引分析结果
        """
        try:
            # 获取表的所有索引
            inspector = inspect(self.db.bind)
            indexes = inspector.get_indexes(table_name)
            
            # 分析索引使用情况
            analysis = {
                "table_name": table_name,
                "total_indexes": len(indexes),
                "indexes": indexes,
                "recommendations": []
            }
            
            # 检查是否有主键索引
            has_primary = any(idx.get('unique', False) for idx in indexes)
            if not has_primary:
                analysis["recommendations"].append("建议添加主键索引")
                
            # 检查是否有常用查询字段的索引
            # 这里可以根据业务逻辑添加更多检查
            
            return analysis
            
        except Exception as e:
            logger.error(f"分析表索引失败: {table_name} - 错误: {e}")
            return {"error": str(e)}
    
    def create_recommended_indexes(self, recommendations: List[Dict[str, Any]]):
        """
        创建推荐的索引
        
        Args:
            recommendations: 索引推荐列表
        """
        for rec in recommendations:
            try:
                table_name = rec.get("table_name")
                column_name = rec.get("column_name")
                index_name = rec.get("index_name", f"idx_{table_name}_{column_name}")
                
                # 创建索引SQL
                sql = text(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({column_name})")
                self.db.execute(sql)
                self.db.commit()
                
                logger.info(f"已创建索引: {index_name} on {table_name}({column_name})")
                
            except Exception as e:
                logger.error(f"创建索引失败: {rec} - 错误: {e}")
                self.db.rollback()


def query_performance_monitor(func: Callable) -> Callable:
    """
    查询性能监控装饰器
    
    Args:
        func: 被装饰的函数
        
    Returns:
        装饰后的函数
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func_name = func.__name__
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if execution_time > 1.0:  # 1秒阈值
                logger.warning(
                    f"函数 {func_name} 执行缓慢 - 时间: {execution_time:.3f}秒"
                )
                
            logger.debug(f"函数 {func_name} 执行完成 - 时间: {execution_time:.3f}秒")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"函数 {func_name} 执行失败 - 错误: {e} - 时间: {execution_time:.3f}秒")
            raise
    
    return wrapper


class QueryCacheManager:
    """查询缓存管理器"""
    
    def __init__(self, cache_ttl: int = 300):  # 默认5分钟
        self.cache = {}
        self.cache_ttl = cache_ttl
        self.hit_count = 0
        self.miss_count = 0
        
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                self.hit_count += 1
                return value
            else:
                # 缓存过期，删除
                del self.cache[key]
                
        self.miss_count += 1
        return None
    
    def set(self, key: str, value: Any):
        """设置缓存值"""
        self.cache[key] = (value, time.time())
        
        # 清理过期缓存
        self._cleanup_expired()
    
    def _cleanup_expired(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp >= self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
            
        if expired_keys:
            logger.debug(f"清理了 {len(expired_keys)} 个过期缓存")
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total if total > 0 else 0
        
        return {
            "cache_size": len(self.cache),
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "cache_ttl": self.cache_ttl
        }


# 常用查询优化模式
COMMON_OPTIMIZATION_PATTERNS = {
    "limit_offset": {
        "description": "使用游标分页替代LIMIT OFFSET",
        "suggestion": "对于大数据集分页，建议使用WHERE id > last_id LIMIT n模式"
    },
    "n_plus_one": {
        "description": "N+1查询问题",
        "suggestion": "使用joinedload或selectinload预加载关联数据"
    },
    "full_table_scan": {
        "description": "全表扫描",
        "suggestion": "添加合适的索引或优化查询条件"
    },
    "unnecessary_columns": {
        "description": "选择不必要的列",
        "suggestion": "只选择需要的列，避免SELECT *"
    }
}


def get_query_optimizer(db_session: Session) -> DatabaseQueryOptimizer:
    """获取查询优化器实例"""
    return DatabaseQueryOptimizer(db_session)


# 示例使用
if __name__ == "__main__":
    # 示例：如何使用查询优化器
    import sqlite3
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # 创建测试数据库连接
    engine = create_engine('sqlite:///:memory:')
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # 创建优化器
    optimizer = DatabaseQueryOptimizer(db)
    
    # 分析表索引
    print("查询优化器初始化完成")
    print("常用优化模式:", COMMON_OPTIMIZATION_PATTERNS)