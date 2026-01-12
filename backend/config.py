from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API配置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "竞彩扫盘工具"
    VERSION: str = "1.0.0"

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./sport_lottery.db"

    # 爬虫配置
    SCRAPERS: List[str] = ["netease", "sina", "tencent"]
    SCRAPE_INTERVAL: int = 1800  # 30分钟
    MAX_RETRY: int = 3

    # 数据源配置
    NETEASE_SPORTS_URL: str = "https://sports.163.com"
    SINA_SPORTS_URL: str = "https://sports.sina.com.cn"
    TENCENT_SPORTS_URL: str = "https://sports.qq.com"

    # 权重配置
    WEIGHTS: dict = {
        "injury": 9.0,
        "weather": 7.5,
        "referee": 7.0,
        "motive": 8.5,
        "tactics": 7.0,
        "coach": 7.5,
        "atmosphere": 6.5,
        "history": 5.0,
        "other": 6.0
    }

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()