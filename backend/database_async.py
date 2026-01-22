"""
异步数据库配置模块
支持异步数据库操作和连接池管理
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool
from backend.config import settings
from typing import AsyncGenerator

# 配置异步数据库引擎
if settings.ASYNC_DATABASE_URL.startswith("sqlite"):
    # SQLite异步配置
    async_engine = create_async_engine(
        settings.ASYNC_DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        poolclass=None,  # SQLite异步不需要连接池
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL/MySQL异步配置
    async_engine = create_async_engine(
        settings.ASYNC_DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        poolclass=QueuePool,
        pool_size=settings.ASYNC_DB_POOL_SIZE,
        max_overflow=settings.ASYNC_DB_MAX_OVERFLOW,
        pool_timeout=settings.ASYNC_DB_POOL_TIMEOUT,
        pool_recycle=settings.ASYNC_DB_POOL_RECYCLE,
        pool_pre_ping=True
    )

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    异步依赖函数获取数据库会话
    使用连接池进行高效的数据库连接管理
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_async_db_engine_info():
    """获取异步数据库引擎池信息用于监控"""
    if hasattr(async_engine.pool, 'size'):
        return {
            "pool_size": async_engine.pool.size(),
            "checked_in": async_engine.pool.checkedin(),
            "checked_out": async_engine.pool.checkedout(),
            "overflow": async_engine.pool.overflow(),
            "invalidated": async_engine.pool.invalidated(),
            "database_url": settings.ASYNC_DATABASE_URL.split('@')[-1] if '@' in settings.ASYNC_DATABASE_URL else settings.ASYNC_DATABASE_URL
        }
    else:
        # SQLite没有连接池
        return {
            "pool_size": 1,
            "checked_in": 1,
            "checked_out": 0,
            "overflow": 0,
            "invalidated": 0,
            "database_url": settings.ASYNC_DATABASE_URL.split('@')[-1] if '@' in settings.ASYNC_DATABASE_URL else settings.ASYNC_DATABASE_URL,
            "note": "SQLite uses StaticPool (single connection)"
        }

async def close_async_engine():
    """关闭异步引擎"""
    await async_engine.dispose()