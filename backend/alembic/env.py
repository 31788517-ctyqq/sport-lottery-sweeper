import sys
import logging
logger = logging.getLogger(__name__)
import os
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# =============================================================================
# 项目路径配置
# =============================================================================
# 获取当前文件(alembic/env.py)的绝对路径
current_file = Path(__file__).resolve()
# 计算项目根目录 (backend的上一级目录)
project_root = current_file.parent.parent.parent
# 将项目根目录添加到Python路径，确保能导入项目模块
sys.path.insert(0, str(project_root))

logger.debug(f"[Alembic] Project root: {project_root}")
logger.debug(f"[Alembic] Python path includes: {project_root}")

# =============================================================================
# 导入项目配置
# =============================================================================
try:
    from backend.config import settings
    logger.debug(f"[Alembic] Successfully loaded settings from backend.config")
    logger.debug(f"[Alembic] Database URL: {settings.DATABASE_URL}")
except ImportError as e:
    logger.debug(f"[Alembic] Failed to import from backend.config: {e}")
    try:
        # 备用导入方式
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "config", 
            project_root / "backend" / "config.py"
        )
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        settings = config_module.settings
        logger.debug(f"[Alembic] Successfully loaded settings via importlib")
    except Exception as e2:
        logger.debug(f"[Alembic] Failed to load settings via importlib: {e2}")
        # 最后的备用方案 - 使用data目录
        from pathlib import Path
        from backend.config import DATA_DIR, ABS_DB_PATH
        class FallbackSettings:
            DATABASE_URL = f"sqlite:///{ABS_DB_PATH}"
            PROJECT_NAME = "Sport Lottery Sweeper (Fallback)"
        
        settings = FallbackSettings()
        logger.debug(f"[Alembic] Using fallback settings")

# =============================================================================
# Alembic配置和日志设置
# =============================================================================
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# =============================================================================
# 导入模型元数据 - 支持自动生成迁移
# =============================================================================
target_metadata = None

# 尝试导入所有模型的Base类
model_imports = [
    "backend.models.base",
    "backend.models.user",
    "backend.models.admin_user", 
    "backend.models.match",
    "backend.models.intelligence_record",
    "backend.models.crawler_config",
]

for module_name in model_imports:
    try:
        module = __import__(module_name, fromlist=["Base"])
        if hasattr(module, "Base"):
            if target_metadata is None:
                target_metadata = module.Base.metadata
            else:
                # 合并所有metadata（如果有多个Base类）
                target_metadata = target_metadata + module.Base.metadata
            logger.debug(f"[Alembic] Successfully imported metadata from {module_name}")
    except ImportError as e:
        logger.debug(f"[Alembic] Warning: Could not import {module_name}: {e}")
    except AttributeError as e:
        logger.debug(f"[Alembic] Warning: No Base class found in {module_name}: {e}")

# 如果没有找到任何metadata，使用fallback
if target_metadata is None:
    logger.debug("[Alembic] Warning: No model metadata found, using empty metadata")
    from sqlalchemy import MetaData
    target_metadata = MetaData()

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    try:
        # 使用项目配置中的数据库URL
        url = settings.DATABASE_URL
        logger.debug(f"[Alembic Offline] Using database URL: {url}")
        
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
            compare_type=True,      # 比较列类型变化
            compare_server_default=True,  # 比较服务器默认值
            render_as_batch=True,   # 支持批量操作（SQLite必需）
        )

        with context.begin_transaction():
            context.run_migrations()
            
        logger.debug("[Alembic Offline] Migrations completed successfully")
        
    except Exception as e:
        logger.debug(f"[Alembic Offline] Error during offline migration: {e}")
        raise


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    try:
        # 使用项目配置中的数据库URL
        DATABASE_URL = settings.DATABASE_URL
        logger.debug(f"[Alembic Online] Original database URL: {DATABASE_URL}")
        
        # Alembic需要同步驱动，所以替换异步驱动名称
        if DATABASE_URL.startswith("sqlite+aiosqlite"):
            # SQLite的异步驱动替换为同步驱动
            DATABASE_URL = DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")
        elif DATABASE_URL.startswith("postgresql+asyncpg"):
            DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
        elif DATABASE_URL.startswith("mysql+aiomysql"):
            DATABASE_URL = DATABASE_URL.replace("mysql+aiomysql", "mysql+pymysql")
        
        logger.debug(f"[Alembic Online] Using sync database URL: {DATABASE_URL}")

        configuration = config.get_section(config.config_ini_section)
        if configuration is None:
            configuration = {}
            
        configuration["sqlalchemy.url"] = DATABASE_URL

        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            echo=False,  # 设置为True可以看到SQL语句
        )

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,           # 比较列类型变化
                compare_server_default=True, # 比较服务器默认值
                render_as_batch=True,        # 支持批量操作（SQLite必需）
            )

            with context.begin_transaction():
                context.run_migrations()
                
            logger.debug("[Alembic Online] Migrations completed successfully")
            
    except Exception as e:
        logger.debug(f"[Alembic Online] Error during online migration: {e}")
        raise


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()