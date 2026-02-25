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
# 椤圭洰璺緞閰嶇疆
# =============================================================================
# 鑾峰彇褰撳墠鏂囦欢(alembic/env.py)鐨勭粷瀵硅矾寰?
current_file = Path(__file__).resolve()
# 璁＄畻椤圭洰鏍圭洰褰?(backend鐨勪笂涓€绾х洰褰?
project_root = current_file.parent.parent.parent
# 灏嗛」鐩牴鐩綍娣诲姞鍒癙ython璺緞锛岀‘淇濊兘瀵煎叆椤圭洰妯″潡
sys.path.insert(0, str(project_root))

logger.debug(f"[Alembic] Project root: {project_root}")
logger.debug(f"[Alembic] Python path includes: {project_root}")

# =============================================================================
# 瀵煎叆椤圭洰閰嶇疆
# =============================================================================
try:
    from backend.config import settings
    logger.debug(f"[Alembic] Successfully loaded settings from backend.config")
    logger.debug(f"[Alembic] Database URL: {settings.DATABASE_URL}")
except ImportError as e:
    logger.debug(f"[Alembic] Failed to import from backend.config: {e}")
    try:
        # 澶囩敤瀵煎叆鏂瑰紡
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
        # 鏈€鍚庣殑澶囩敤鏂规 - 浣跨敤data鐩綍
        from pathlib import Path
        from backend.config import DATA_DIR, ABS_DB_PATH
        class FallbackSettings:
            DATABASE_URL = f"sqlite:///{ABS_DB_PATH}"
            PROJECT_NAME = "Sport Lottery Sweeper (Fallback)"
        
        settings = FallbackSettings()
        logger.debug(f"[Alembic] Using fallback settings")

# =============================================================================
# Alembic閰嶇疆鍜屾棩蹇楄缃?
# =============================================================================
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# =============================================================================
# 瀵煎叆妯″瀷鍏冩暟鎹?- 鏀寔鑷姩鐢熸垚杩佺Щ
# =============================================================================
target_metadata = None

# 灏濊瘯瀵煎叆鎵€鏈夋ā鍨嬬殑Base绫?
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
                # 鍚堝苟鎵€鏈塵etadata锛堝鏋滄湁澶氫釜Base绫伙級
                pass
            logger.debug(f"[Alembic] Successfully imported metadata from {module_name}")
    except ImportError as e:
        logger.debug(f"[Alembic] Warning: Could not import {module_name}: {e}")
    except AttributeError as e:
        logger.debug(f"[Alembic] Warning: No Base class found in {module_name}: {e}")

# 濡傛灉娌℃湁鎵惧埌浠讳綍metadata锛屼娇鐢╢allback
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
        # 浣跨敤椤圭洰閰嶇疆涓殑鏁版嵁搴揢RL
        url = settings.DATABASE_URL
        logger.debug(f"[Alembic Offline] Using database URL: {url}")
        
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
            compare_type=True,      # 姣旇緝鍒楃被鍨嬪彉鍖?
            compare_server_default=True,  # 姣旇緝鏈嶅姟鍣ㄩ粯璁ゅ€?
            render_as_batch=True,   # 鏀寔鎵归噺鎿嶄綔锛圫QLite蹇呴渶锛?
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
        # 浣跨敤椤圭洰閰嶇疆涓殑鏁版嵁搴揢RL
        DATABASE_URL = settings.DATABASE_URL
        logger.debug(f"[Alembic Online] Original database URL: {DATABASE_URL}")
        
        # Alembic闇€瑕佸悓姝ラ┍鍔紝鎵€浠ユ浛鎹㈠紓姝ラ┍鍔ㄥ悕绉?
        if DATABASE_URL.startswith("sqlite+aiosqlite"):
            # SQLite鐨勫紓姝ラ┍鍔ㄦ浛鎹负鍚屾椹卞姩
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
            echo=False,  # 璁剧疆涓篢rue鍙互鐪嬪埌SQL璇彞
        )

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,           # 姣旇緝鍒楃被鍨嬪彉鍖?
                compare_server_default=True, # 姣旇緝鏈嶅姟鍣ㄩ粯璁ゅ€?
                render_as_batch=True,        # 鏀寔鎵归噺鎿嶄綔锛圫QLite蹇呴渶锛?
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
