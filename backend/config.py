from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import secrets
from pathlib import Path
import os
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

# 项目根目录 - 使用当前文件所在目录
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)  # 确保data目录存在
DATABASE_PATH = DATA_DIR / "sport_lottery.db"

# 计算数据库URL（在类定义外部）- 使用绝对路径
ABS_DB_PATH = str(DATABASE_PATH.absolute())
# 规范化路径分隔符，确保Windows兼容性
if ':' in ABS_DB_PATH:
    # Windows路径格式：C:\path\to\file.db -> ///C:/path/to/file.db
    ABS_DB_PATH = ABS_DB_PATH.replace('\\\\', '/')
    DEFAULT_DATABASE_URL = f"sqlite:///{ABS_DB_PATH}"
    DEFAULT_ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{ABS_DB_PATH}"
else:
    # Unix路径格式
    DEFAULT_DATABASE_URL = f"sqlite:///{ABS_DB_PATH}"
    DEFAULT_ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{ABS_DB_PATH}"

# 调试输出（可选，避免编码问题）
try:
    print(f"数据库路径配置: {DEFAULT_DATABASE_URL}")
except UnicodeEncodeError:
    print(f"Database URL configured: {DEFAULT_DATABASE_URL}")


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
    # Generate secure secret key from environment variable or create random one
    SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv(
            "SECRET_KEY", 
            secrets.token_urlsafe(32)  # Fallback to random 32-byte key
        ),
        description="Secret key for encryption - should be set via SECRET_KEY env var in production"
    )

    # --- Backend CORS Origins ---
    # Security: Explicit origins instead of wildcard to prevent unauthorized domains
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",      # Frontend development server
        "http://127.0.0.1:3000",      # Frontend alternative
        "http://localhost:8080",      # Alternative frontend port
        "https://your-production-domain.com",  # Production domain - UPDATE THIS
        "https://www.your-production-domain.com"  # Production www domain - UPDATE THIS
    ]

    # --- JWT Settings ---
    # Shortened expiry times for enhanced security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Reduced from 30 to 15 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1    # Reduced from 7 to 1 day for security
    ALGORITHM: str = "HS256"  # JWT algorithm
    
    # Token blacklist settings
    ENABLE_TOKEN_BLACKLIST: bool = Field(
        default=True, 
        description="Enable token blacklist for logout/invalidation functionality"
    )
    BLACKLIST_CLEANUP_HOURS: int = Field(
        default=24, 
        description="Hours to keep blacklisted tokens before cleanup"
    )

    # --- Database Pool Settings ---
    # Connection pool sizes
    DB_POOL_SIZE: int = Field(default=20, description="Number of connections to keep in pool")
    DB_MAX_OVERFLOW: int = Field(default=40, description="Maximum overflow connections allowed")
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
    ASYNC_DB_POOL_SIZE: int = Field(default=20, description="Async pool size")
    ASYNC_DB_MAX_OVERFLOW: int = Field(default=40, description="Async max overflow")
    ASYNC_DB_POOL_TIMEOUT: int = Field(default=30, description="Async pool timeout")
    ASYNC_DB_POOL_RECYCLE: int = Field(default=3600, description="Async pool recycle")

    # --- Redis Settings ---
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    REDIS_POOL_SIZE: int = Field(default=10, description="Redis connection pool size")
    REDIS_MAX_CONNECTIONS: int = Field(default=20, description="Max Redis connections")

    # --- Pool Reconcile Settings ---
    POOL_RECONCILE_ENABLED: bool = Field(
        default=True,
        description="Enable periodic pool reconcile task",
    )
    POOL_RECONCILE_INTERVAL_SECONDS: int = Field(
        default=60,
        description="Pool reconcile interval in seconds",
    )
    POOL_RECONCILE_DRY_RUN: bool = Field(
        default=True,
        description="Run reconcile in dry-run mode by default",
    )

    # --- IP Pool Capacity Targets ---
    IP_POOL_TARGET_ACTIVE: int = Field(default=60, description="Target active proxy count")
    IP_POOL_TARGET_STANDBY: int = Field(default=20, description="Target standby proxy count")
    IP_POOL_FAILURES_BEFORE_COOLING: int = Field(
        default=5,
        description="Failure threshold before moving proxy to cooling status",
    )
    IP_POOL_EXPECTED_ACTIVE_PER_FETCH_PAGE: int = Field(
        default=5,
        description="Expected active proxies per fetch page",
    )
    IP_POOL_AUTO_REPLENISH_ENABLED: bool = Field(
        default=False,
        description="Enable automatic IP pool replenishment",
    )

    # --- Headers Pool Capacity Targets ---
    HEADER_POOL_HEADERS_PER_ACTIVE_IP: int = Field(
        default=3,
        description="Target headers per active proxy",
    )
    HEADER_POOL_MIN_ACTIVE_PER_DOMAIN: int = Field(
        default=30,
        description="Minimum enabled headers for each domain",
    )
    HEADER_POOL_LOW_QUALITY_MIN_USAGE: int = Field(
        default=20,
        description="Minimum usage count before quality check",
    )
    HEADER_POOL_LOW_QUALITY_SUCCESS_RATE: float = Field(
        default=70.0,
        description="Headers with lower success rate are considered low quality",
    )
    HEADER_POOL_AUTO_REPLENISH_ENABLED: bool = Field(
        default=False,
        description="Enable automatic headers pool replenishment",
    )
    HEADER_POOL_MIN_BINDINGS_PER_SOURCE: int = Field(
        default=6,
        description="Minimum headers binding count per data source",
    )

    # --- Runtime Request Fallback Settings ---
    REQUEST_USE_PROXY_BY_DEFAULT: bool = Field(
        default=True,
        description="Use proxy first for crawler HTTP requests",
    )
    REQUEST_ALLOW_DIRECT_FALLBACK: bool = Field(
        default=True,
        description="Allow direct request fallback when proxy is unavailable",
    )
    REQUEST_PROXY_REUSE_MIN_SECONDS: int = Field(
        default=15,
        description="Minimum seconds before reusing same proxy in scheduler requests",
    )
    REQUEST_DOMAIN_FAILURE_THRESHOLD: int = Field(
        default=5,
        description="Failure threshold to open domain circuit breaker",
    )
    REQUEST_DOMAIN_COOLDOWN_SECONDS: int = Field(
        default=300,
        description="Domain circuit breaker cooldown window in seconds",
    )

    # --- Auto 500w -> 100qiu Sync Settings ---
    AUTO_100QIU_SYNC_ENABLED: bool = Field(
        default=True,
        description="Enable automatic 500w issue discovery and 100qiu fetch",
    )
    AUTO_100QIU_BASE_INTERVAL_HOURS: int = Field(
        default=3,
        description="Base interval hours for automatic issue discovery",
    )
    AUTO_100QIU_WINDOW_ENABLED: bool = Field(
        default=True,
        description="Enable windowed high-frequency discovery schedule",
    )
    AUTO_100QIU_WINDOW_HOURS: str = Field(
        default="10-23",
        description="Cron hour expression for windowed discovery schedule",
    )
    AUTO_100QIU_WINDOW_MINUTE_STEP: int = Field(
        default=30,
        description="Minute step for windowed discovery schedule",
    )
    AUTO_100QIU_SOURCE_UPDATE_FREQUENCY_MINUTES: int = Field(
        default=180,
        description="update_frequency value for auto-created 100qiu sources",
    )

    # --- Auto Entity Mapping Sync Settings ---
    AUTO_ENTITY_MAPPING_SYNC_ENABLED: bool = Field(
        default=True,
        description="Enable periodic DB-driven entity mapping synchronization",
    )
    AUTO_ENTITY_MAPPING_SYNC_INTERVAL_MINUTES: int = Field(
        default=180,
        description="Interval minutes for entity mapping synchronization",
    )
    AUTO_ENTITY_MAPPING_SYNC_RUN_ON_STARTUP: bool = Field(
        default=True,
        description="Run one entity mapping synchronization after startup",
    )
    AUTO_ENTITY_MAPPING_SYNC_MATCH_SCAN_LIMIT: int = Field(
        default=50000,
        description="Maximum recent match rows scanned per sync run for alias extraction",
    )

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

    @field_validator("DEBUG", mode="before")
    def parse_debug(cls, v):
        if isinstance(v, str):
            lowered = v.strip().lower()
            if lowered in {"release", "prod", "production"}:
                return False
        return v

    @field_validator("DATABASE_URL", mode='before')
    def validate_database_url(cls, v):
        """Validate database URL and strip unsupported SQLAlchemy pool query params."""
        if v is None or str(v).strip() == "":
            return DEFAULT_DATABASE_URL

        v = str(v)
        if v.startswith("sqlite"):
            # 对 sqlite：统一使用项目根目录下的绝对路径，避免相对路径因工作目录不同导致“unable to open database file”
            return DEFAULT_DATABASE_URL
        elif v.startswith("postgresql"):
            # Keep DSN clean; connection pool must be configured via create_engine kwargs.
            parsed = urlparse(v)
            blocked = {"pool_size", "max_overflow", "pool_timeout", "pool_recycle", "pool_pre_ping"}
            kept = [(k, val) for k, val in parse_qsl(parsed.query, keep_blank_values=True) if k not in blocked]
            return urlunparse(parsed._replace(query=urlencode(kept)))
        return v

    @field_validator("ASYNC_DATABASE_URL", mode='before')
    def validate_async_database_url(cls, v):
        if v is None or str(v).strip() == "":
            return DEFAULT_ASYNC_DATABASE_URL

        v = str(v)
        if v.startswith("sqlite"):
            return DEFAULT_ASYNC_DATABASE_URL
        return v

    # 使用项目根目录下的 .env，避免因工作目录不同导致读取不到配置（尤其是 SECRET_KEY）
    model_config = SettingsConfigDict(env_file=str(PROJECT_ROOT / ".env"), env_file_encoding="utf-8", extra="ignore")


settings = Settings()
