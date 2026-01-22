from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import secrets
from pathlib import Path

# 动态获取项目根目录（config.py 位于 backend/ 目录下）
PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_PATH = PROJECT_ROOT / "sport_lottery.db"


class Settings(BaseSettings):
    # --- Project Info ---
    PROJECT_NAME: str = "Sport Lottery Sweeper System"
    PROJECT_NAME_CN: str = "竞彩足球扫盘系统"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Sport Lottery Sweeper System API"

    # --- API Settings ---
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    DOCS_ENABLED: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # --- Security Settings ---
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # --- JWT Settings ---
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Database Pool Settings ---
    # Connection pool sizes
    DB_POOL_SIZE: int = Field(default=5, description="Number of connections to keep in pool")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Maximum overflow connections allowed")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Seconds to wait for connection from pool")
    DB_POOL_RECYCLE: int = Field(default=3600, description="Recycle connections after seconds")
    DB_POOL_PRE_PING: bool = Field(default=True, description="Enable connection health checks")
    
    # --- Database Settings ---
    DATABASE_URL: str = f"sqlite:///{DATABASE_PATH}"
    DATABASE_ECHO: bool = False

    # --- Async Database Settings ---
    ASYNC_DATABASE_URL: str = f"sqlite+aiosqlite:///{DATABASE_PATH}"
    
    # Async connection pool settings
    ASYNC_DB_POOL_SIZE: int = Field(default=5, description="Async pool size")
    ASYNC_DB_MAX_OVERFLOW: int = Field(default=10, description="Async max overflow")
    ASYNC_DB_POOL_TIMEOUT: int = Field(default=30, description="Async pool timeout")
    ASYNC_DB_POOL_RECYCLE: int = Field(default=3600, description="Async pool recycle")

    # --- Redis Settings ---
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_POOL_SIZE: int = Field(default=10, description="Redis connection pool size")
    REDIS_MAX_CONNECTIONS: int = Field(default=20, description="Max Redis connections")

    # --- Logging Settings ---
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE_MAX_BYTES: int = Field(default=10485760, description="Max bytes per log file (10MB)")
    LOG_BACKUP_COUNT: int = Field(default=30, description="Number of backup files to keep")
    LOG_ROTATION_INTERVAL: str = Field(default="midnight", description="Log rotation interval")
    LOG_ENCODING: str = Field(default="utf-8", description="Log file encoding")
    LOG_CLEANUP_ENABLED: bool = Field(default=True, description="Enable automatic cleanup of old logs")
    LOG_ERROR_BACKUP_MULTIPLIER: int = Field(default=2, description="Error log backup multiplier")
    LOG_ACCESS_ROTATION: str = Field(default="H", description="Access log rotation interval")
    LOG_ACCESS_BACKUP_COUNT: int = Field(default=168, description="Access log backup count")

    # --- Backend CORS Origins ---
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v):
        """Validate and enhance database URL with pool settings"""
        if v.startswith("sqlite"):
            return v
        elif v.startswith("postgresql"):
            # Add pool settings for PostgreSQL
            if "?" not in v:
                v += "?"
            else:
                v += "&"
            pool_params = f"pool_size={cls.DB_POOL_SIZE}&max_overflow={cls.DB_MAX_OVERFLOW}&pool_timeout={cls.DB_POOL_TIMEOUT}&pool_recycle={cls.DB_POOL_RECYCLE}&pool_pre_ping={str(cls.DB_POOL_PRE_PING).lower()}"
            return v + pool_params
        return v

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()