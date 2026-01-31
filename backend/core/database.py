from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import configure_mappers
from sqlalchemy.event import listens_for
from sqlalchemy.orm.mapper import Mapper
from typing import AsyncGenerator, Dict, Any
# AI_WORKING: coder1 @2026-01-26 - 修复相对导入错误，使用绝对导入
from backend.config import settings
# AI_WORKING: coder1 @2026-01-26 - 使用与模型相同的Base类，确保表创建正确
from backend.models.base import Base

# 同步数据库配置
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base已从backend.models.base导入
# AI_DONE: coder1 @2026-01-26

# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建数据库表
# AI_WORKING: coder1 @2026-01-26 - 导入所有模型以确保它们注册到Base.metadata
def create_tables():
    # 导入所有模型，确保它们注册到Base.metadata
    from backend.models import (
        user, match, intelligence, venues, predictions, odds, data_review,
        admin_user, data, system_config, crawler_config, crawler_alert_rules,
        crawler_alert_records, crawler_metrics, intelligence_record,
        crawler_tasks, crawler_logs, data_sources, matches, odds_companies,
        sp_records, sp_modification_logs, draw_feature, draw_training_job,
        draw_model_version, draw_prediction_result, log_entry
    )
    
    print(f"✅ 已导入模型，共有 {len(Base.metadata.tables)} 张表需要创建")
    Base.metadata.create_all(bind=engine)


def setup_relationships():
    """
    设置模型之间的关系，避免循环导入问题
    注意：模型关系已在各自的模型文件中定义，此处不再重复设置
    """
    # 模型关系已在各自的模型文件中定义，无需重复设置
    # 此函数保留为空，仅为了保持现有代码结构
    pass


@listens_for(Mapper, 'after_configured', once=True)
def setup_models_relationships():
    """
    在所有模型配置完成后设置关系
    这样可以避免模型间的循环导入问题
    """
    setup_relationships()
    # 确保所有映射器都已正确配置，包括动态添加的关系
    configure_mappers()


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