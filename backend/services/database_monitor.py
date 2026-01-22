"""
数据库监控服务
提供连接池状态监控和健康检查功能
"""
from sqlalchemy import text
from backend.database import engine, get_db_engine_info
from backend.database_async import async_engine, get_async_db_engine_info
from backend.config import settings
from datetime import datetime
import asyncio

class DatabaseMonitor:
    """数据库监控类"""
    
    @staticmethod
    def get_connection_pool_status():
        """获取同步数据库连接池状态"""
        try:
            pool_info = get_db_engine_info()
            
            # 测试数据库连接
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                db_status = "healthy"
        except Exception as e:
            pool_info = {
                "error": str(e),
                "database_url": settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL
            }
            db_status = "unhealthy"
        
        return {
            "status": db_status,
            "timestamp": datetime.now().isoformat(),
            "sync_pool": pool_info,
            "database_type": "sqlite" if settings.DATABASE_URL.startswith("sqlite") else "postgresql" if settings.DATABASE_URL.startswith("postgresql") else "mysql" if settings.DATABASE_URL.startswith("mysql") else "unknown"
        }
    
    @staticmethod
    async def get_async_connection_pool_status():
        """获取异步数据库连接池状态"""
        try:
            pool_info = await get_async_db_engine_info()
            
            # 测试异步数据库连接
            async with async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                db_status = "healthy"
        except Exception as e:
            pool_info = {
                "error": str(e),
                "database_url": settings.ASYNC_DATABASE_URL.split('@')[-1] if '@' in settings.ASYNC_DATABASE_URL else settings.ASYNC_DATABASE_URL
            }
            db_status = "unhealthy"
        
        return {
            "status": db_status,
            "timestamp": datetime.now().isoformat(),
            "async_pool": pool_info,
            "database_type": "sqlite" if settings.ASYNC_DATABASE_URL.startswith("sqlite") else "postgresql" if settings.ASYNC_DATABASE_URL.startswith("postgresql") else "mysql" if settings.ASYNC_DATABASE_URL.startswith("mysql") else "unknown"
        }
    
    @staticmethod
    def get_database_statistics():
        """获取数据库统计信息"""
        try:
            # 获取表统计信息
            inspector = engine.dialect.get_inspector(engine)
            tables = inspector.get_table_names()
            
            table_stats = {}
            for table_name in tables:
                try:
                    result = engine.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.scalar()
                    table_stats[table_name] = {
                        "row_count": count,
                        "columns": [col['name'] for col in inspector.get_columns(table_name)]
                    }
                except Exception as e:
                    table_stats[table_name] = {
                        "error": str(e)
                    }
            
            return {
                "total_tables": len(tables),
                "tables": table_stats,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    @classmethod
    def get_comprehensive_health_report(cls):
        """获取综合健康报告"""
        sync_status = cls.get_connection_pool_status()
        db_stats = cls.get_database_statistics()
        
        # 计算健康评分
        health_score = 100
        issues = []
        
        if sync_status["status"] != "healthy":
            health_score -= 50
            issues.append("同步数据库连接异常")
        
        if "error" in db_stats:
            health_score -= 30
            issues.append("无法获取数据库统计信息")
        
        if settings.DATABASE_URL.startswith("sqlite"):
            # SQLite单连接模式警告
            if sync_status["sync_pool"].get("pool_size", 0) > 1:
                issues.append("SQLite建议使用单连接模式")
        else:
            # 检查连接池使用情况
            pool_size = sync_status["sync_pool"].get("pool_size", 0)
            checked_out = sync_status["sync_pool"].get("checked_out", 0)
            if pool_size > 0 and checked_out / pool_size > 0.8:
                health_score -= 20
                issues.append("数据库连接池使用率过高")
        
        return {
            "overall_health_score": max(0, health_score),
            "status": "healthy" if health_score > 70 else "warning" if health_score > 40 else "critical",
            "issues": issues,
            "sync_database": sync_status,
            "database_statistics": db_stats,
            "configuration": {
                "db_pool_size": settings.DB_POOL_SIZE,
                "db_max_overflow": settings.DB_MAX_OVERFLOW,
                "db_pool_timeout": settings.DB_POOL_TIMEOUT,
                "db_pool_recycle": settings.DB_POOL_RECYCLE,
                "database_echo": settings.DATABASE_ECHO
            },
            "timestamp": datetime.now().isoformat()
        }

# 全局监控实例
db_monitor = DatabaseMonitor()