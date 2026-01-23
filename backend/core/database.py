from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import AsyncGenerator
from ..config import settings

# 同步数据库配置
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建数据库表
def create_tables():
    Base.metadata.create_all(bind=engine)


async def init_db(app):
    """
    初始化数据库连接
    """
    # 如果需要异步数据库操作，这里可以初始化
    print("Database initialized")


async def close_db(app):
    """
    关闭数据库连接
    """
    # 如果需要关闭连接池等操作，这里可以处理
    print("Database closed")


# 保持与旧代码的兼容性
def get_db_session():
    """
    获取数据库会话，用于与其他模块的兼容
    """
    return get_db()