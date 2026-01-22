from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import secrets


class Settings(BaseSettings):
    # --- Project Info ---
    PROJECT_NAME: str = "Sport Lottery Sweeper System"
    PROJECT_NAME_CN: str = "竞彩足球扫盘系统"  # Chinese name for reference
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Sport Lottery Sweeper System API"

    # --- API Settings ---
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True  # 设置为True以启用调试模式
    DOCS_ENABLED: bool = True
    HOST: str = "0.0.0.0"  # 改为0.0.0.0允许外部访问
    PORT: int = 8000

    # --- Security Settings ---
    SECRET_KEY: str = Field(default=secrets.token_urlsafe(32), description="Secret key for signing JWT tokens and other security purposes")

    # --- Database Settings ---
    DATABASE_URL: str = Field(default="sqlite:///./sport_lottery.db", description="Database connection string (e.g., postgresql+asyncpg://user:pass@host:port/db)")
    DATABASE_ECHO: bool = False # Set to True to echo SQL queries in logs

    # --- Async Database Settings (using asyncpg) ---
    # These can be derived from database_url but kept separate for clarity if needed    
    ASYNC_DATABASE_URL: Optional[str] = Field(default="sqlite+aiosqlite:///./sport_lottery.db", description="Async database connection string, defaults to database_url")

    # --- Redis Settings ---
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = Field(None, description="Redis password, leave empty if not set")
    REDIS_DB: int = 0

    # --- Backend CORS Origins ---
    BACKEND_CORS_ORIGINS: List[str] = Field(default=["*"], description="A list of origins that are allowed to access the API")

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()