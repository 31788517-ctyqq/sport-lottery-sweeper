#!/usr/bin/env python3
"""数据库连接和基础配置"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 数据库URL配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()

# 依赖注入函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# SQLite 数据库引擎信息函数（简化版）
def get_db_engine_info():
    """
    获取SQLite数据库引擎信息
    由于SQLite不支持连接池，返回基本信息
    """
    from sqlalchemy import text
    import sqlite3
    
    try:
        # 从DATABASE_URL解析数据库路径
        db_path = DATABASE_URL.replace('sqlite:///', '')
        if db_path.startswith('./'):
            db_path = db_path[2:]
        
        # 获取数据库文件信息
        db_size = 0
        try:
            db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
        except:
            pass
        
        # SQLite 连接信息（SQLite没有连接池概念）
        return {
            "driver": "sqlite",
            "database_url": DATABASE_URL,
            "database_path": db_path,
            "database_size_bytes": db_size,
            "database_size_mb": round(db_size / (1024 * 1024), 2) if db_size > 0 else 0,
            "pool_size": 1,  # SQLite 单连接
            "max_overflow": 0,
            "pool_timeout": None,
            "pool_recycle": None,
            "pool_pre_ping": False,
            "check_same_thread": True,
            "echo": False,
            "status": "active",
            "note": "SQLite does not support connection pooling like PostgreSQL/MySQL"
        }
    except Exception as e:
        return {
            "driver": "sqlite",
            "database_url": DATABASE_URL,
            "error": str(e),
            "status": "error"
        }