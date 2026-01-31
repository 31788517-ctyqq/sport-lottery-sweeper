"""
爬虫配置加载器
用于加载和管理爬虫配置
"""
import os
import json
from typing import Dict, Any, Optional
from .enhanced_engine import EnhancedScraperEngine


def get_default_config() -> Dict[str, Any]:
    """
    获取默认配置
    """
    return {
        "max_connections": 100,
        "timeout": 15,
        "max_retries": 3,
        "rate_limit": 10,
        "enable_cache": True,
        "cache_ttl": 300,
        "use_dynamic_proxies": True,
        "proxy_refresh_interval": 300
    }


def load_config_from_env() -> Dict[str, Any]:
    """
    从环境变量加载配置
    """
    config = get_default_config()
    
    # 从环境变量覆盖配置
    if os.getenv("SCRAPER_MAX_CONNECTIONS"):
        config["max_connections"] = int(os.getenv("SCRAPER_MAX_CONNECTIONS"))
    
    if os.getenv("SCRAPER_TIMEOUT"):
        config["timeout"] = int(os.getenv("SCRAPER_TIMEOUT"))
    
    if os.getenv("SCRAPER_MAX_RETRIES"):
        config["max_retries"] = int(os.getenv("SCRAPER_MAX_RETRIES"))
    
    if os.getenv("SCRAPER_RATE_LIMIT"):
        config["rate_limit"] = int(os.getenv("SCRAPER_RATE_LIMIT"))
    
    if os.getenv("SCRAPER_ENABLE_CACHE"):
        config["enable_cache"] = os.getenv("SCRAPER_ENABLE_CACHE").lower() == "true"
    
    if os.getenv("SCRAPER_CACHE_TTL"):
        config["cache_ttl"] = int(os.getenv("SCRAPER_CACHE_TTL"))
    
    if os.getenv("SCRAPER_USE_DYNAMIC_PROXIES"):
        config["use_dynamic_proxies"] = os.getenv("SCRAPER_USE_DYNAMIC_PROXIES").lower() == "true"
    
    if os.getenv("SCRAPER_PROXY_REFRESH_INTERVAL"):
        config["proxy_refresh_interval"] = int(os.getenv("SCRAPER_PROXY_REFRESH_INTERVAL"))
    
    return config


def create_enhanced_engine_from_config(config: Optional[Dict[str, Any]] = None) -> EnhancedScraperEngine:
    """
    根据配置创建增强型爬虫引擎
    """
    if config is None:
        config = load_config_from_env()
    
    return EnhancedScraperEngine(
        max_connections=config.get("max_connections", 100),
        timeout=config.get("timeout", 15),
        max_retries=config.get("max_retries", 3),
        rate_limit=config.get("rate_limit", 10),
        enable_cache=config.get("enable_cache", True),
        cache_ttl=config.get("cache_ttl", 300),
        use_dynamic_proxies=config.get("use_dynamic_proxies", True),
        proxy_refresh_interval=config.get("proxy_refresh_interval", 300)
    )


def get_anti_crawler_config() -> Dict[str, Any]:
    """
    获取反爬虫配置
    """
    return {
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        },
        "delay_range": (1, 3),  # 请求延迟范围（秒）
        "retry_attempts": 3,     # 重试次数
        "use_proxy": True        # 是否使用代理
    }
