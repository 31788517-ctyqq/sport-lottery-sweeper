from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool, StaticPool
from backend.models import Base  # 从 backend.models 导入 Base
from backend.config import settings

# Configure connection pool based on database type
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # SQLite works best with StaticPool
        echo=settings.DATABASE_ECHO
    )
else:
    # PostgreSQL/MySQL configuration with connection pooling
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        pool_pre_ping=settings.DB_POOL_PRE_PING,
        echo=settings.DATABASE_ECHO
    )

# 自动创建所有表
Base.metadata.create_all(bind=engine)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False  # Recommended for FastAPI
)

def get_db():
    """
    Dependency function to get database session with automatic cleanup.
    Uses connection pool for efficient database connection management.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_db_engine_info():
    """Get database engine pool information for monitoring"""
    return {
        "pool_size": getattr(engine.pool, 'size', lambda: 0)(),
        "checked_in": getattr(engine.pool, 'checkedin', lambda: 0)(),
        "checked_out": getattr(engine.pool, 'checkedout', lambda: 0)(),
        "overflow": getattr(engine.pool, 'overflow', lambda: 0)(),
        "invalidated": getattr(engine.pool, 'invalidated', lambda: 0)(),
        "database_url": settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL
    }