from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import secrets
from pathlib import Path
import os

# 项目根目录 - 使用当前文件所在目录
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)  # 确保data目录存在
DATABASE_PATH = DATA_DIR / "sport_lottery.db"

# 计算数据库URL（在类定义外部）- 使用绝对路径
ABS_DB_PATH = str(DATABASE_PATH.absolute()).replace(chr(92), '/')

# 默认数据库URL常量（在类定义之前定义）
DEFAULT_DATABASE_URL = f"sqlite:///{ABS_DB_PATH}"
DEFAULT_ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{ABS_DB_PATH}"


class Settings(BaseSettings):
    # --- Project Info ---
    PROJECT_NAME: str = "Sport Lottery Sweeper System"
    PROJECT_NAME_CN: str = "竞彩足球扫盘系统"
    VERSION: str = "0.2.0"
    DESCRIPTION: str = "\n🏆 Sport Lottery Sweeper System API\n\n一个专业的竞彩足球数据分析和管理平台，提供：\n- 📊 实时比赛数据抓取和分析\n- 🤖 智能预测算法\n- 👥 多角色用户管理\n- 📈 数据可视化和报表\n- 🔐 JWT安全认证\n- 📱 RESTful API设计\n\n## 主要功能模块\n- **用户管理**: 管理员和普通用户的注册、登录、权限管理\n- **比赛管理**: 足球比赛的实时数据抓取、存储、查询\n- **智能分析**: 基于AI的预测算法和数据挖掘\n- **爬虫系统**: 多源数据采集和清洗\n- **监控面板**: 系统状态和性能指标实时监控\n"

    # --- API Settings ---
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    DOCS_ENABLED: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # --- Frontend URL Settings ---
    FRONTEND_BASE_URL: str = "http://localhost:3000"  # 设置为前端运行的端口

    # --- Documentation Settings ---
    API_TITLE: str = "Sport Lottery Sweeper API"
    API_SUMMARY: str = "竞彩足球扫盘系统RESTful API"
    API_CONTACT_NAME: str = "开发团队"
    API_CONTACT_EMAIL: str = "dev@sportlottery.com"
    API_CONTACT_URL: str = "https://github.com/sport-lottery-sweeper"
    API_LICENSE_NAME: str = "MIT"
    API_LICENSE_URL: str = "https://opensource.org/licenses/MIT"

    # --- Swagger UI Settings ---
    SWAGGER_UI_PARAMETERS: dict = {
        "defaultModelsExpandDepth": -1,  # 默认折叠所有模型
        "displayRequestDuration": True,   # 显示请求耗时
        "filter": True,                   # 启用过滤功能
        "showExtensions": True,           # 显示扩展信息
        "showCommonExtensions": True,     # 显示通用扩展
        "tryItOutEnabled": True,          # 启用Try it out功能
    }

    # --- Security Settings ---
    SECRET_KEY: str = Field(default="C_Ks04hg6nT8NC3ZEKG6pQsm7jC_2shXMMm9nhhTY1M=", description="Secret key for encryption")

    # --- Backend CORS Origins ---
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # --- JWT Settings ---
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"  # 添加JWT算法设置

    # --- Database Pool Settings ---
    # Connection pool sizes
    DB_POOL_SIZE: int = Field(default=5, description="Number of connections to keep in pool")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Maximum overflow connections allowed")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Seconds to wait for connection from pool")
    DB_POOL_RECYCLE: int = Field(default=3600, description="Recycle connections after seconds")
    DB_POOL_PRE_PING: bool = Field(default=True, description="Enable connection health checks")
    
    # --- Database Settings ---
    # 从环境变量读取数据库URL，如果没有则使用data目录下的SQLite
    DATABASE_URL: str = Field(
        default=DEFAULT_DATABASE_URL,
        description="Database connection URL"
    )
    DATABASE_ECHO: bool = False

    # --- Async Database Settings ---
    # 同样从环境变量读取异步数据库URL
    ASYNC_DATABASE_URL: str = Field(
        default=DEFAULT_ASYNC_DATABASE_URL,
        description="Async database connection URL"
    )
    
    # Async connection pool settings
    ASYNC_DB_POOL_SIZE: int = Field(default=5, description="Async pool size")
    ASYNC_DB_MAX_OVERFLOW: int = Field(default=10, description="Async max overflow")
    ASYNC_DB_POOL_TIMEOUT: int = Field(default=30, description="Async pool timeout")
    ASYNC_DB_POOL_RECYCLE: int = Field(default=3600, description="Async pool recycle")

    # --- Redis Settings ---
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
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

    # --- Redis URL ---
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    @field_validator("DATABASE_URL", mode='before')
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