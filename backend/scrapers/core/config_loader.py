"""
反爬虫配置加载器
从环境变量和配置文件加载反爬虫设置
"""
import os
import logging
from typing import List, Optional, Dict, Any
from .engine_enhanced import EnhancedScraperEngine

logger = logging.getLogger(__name__)


class AntiCrawlerConfig:
    """反爬虫配置类"""
    
    def __init__(self):
        """从环境变量加载配置"""
        self.load_config()
    
    def load_config(self):
        """加载所有反爬虫相关配置"""
        
        # 代理配置
        self.proxy_enabled = self._get_bool_env('PROXY_POOL_ENABLED', True)
        self.proxy_urls = self._get_list_env('PROXY_URLS', [])
        self.proxy_health_check_interval = self._get_int_env('PROXY_HEALTH_CHECK_INTERVAL', 300)
        self.proxy_ban_duration = self._get_int_env('PROXY_BAN_DURATION', 1800)
        self.proxy_min_score = self._get_float_env('PROXY_MIN_SCORE', 20.0)
        
        # Cookie配置
        self.cookie_enabled = self._get_bool_env('COOKIE_ENABLED', True)
        self.cookie_file = self._get_str_env('COOKIE_FILE', './cookies.json')
        
        # 请求头配置
        self.header_profile = self._get_str_env('HEADER_PROFILE', 'chrome_desktop')
        self.enable_fingerprint = self._get_bool_env('ENABLE_FINGERPRINT', True)
        self.header_rotation_interval = self._get_int_env('HEADER_ROTATION_INTERVAL', 50)
        
        # 浏览器指纹配置
        self.enable_canvas_fingerprint = self._get_bool_env('ENABLE_CANVAS_FINGERPRINT', True)
        self.enable_webgl_fingerprint = self._get_bool_env('ENABLE_WEBGL_FINGERPRINT', True)
        self.screen_resolutions = self._get_list_env(
            'SCREEN_RESOLUTIONS', 
            ['1920x1080', '1366x768', '1440x900', '1536x864', '2560x1440']
        )
        self.timezones = self._get_list_env(
            'TIMEZONES', 
            ['Asia/Shanghai', 'Asia/Beijing', 'UTC+8', 'GMT+0800']
        )
        
        logger.info("反爬虫配置加载完成")
        self._log_config()
    
    def _get_str_env(self, key: str, default: str = '') -> str:
        """获取字符串环境变量"""
        return os.getenv(key, default)
    
    def _get_int_env(self, key: str, default: int = 0) -> int:
        """获取整数环境变量"""
        try:
            return int(os.getenv(key, default))
        except ValueError:
            logger.warning(f"环境变量 {key} 格式错误，使用默认值: {default}")
            return default
    
    def _get_float_env(self, key: str, default: float = 0.0) -> float:
        """获取浮点数环境变量"""
        try:
            return float(os.getenv(key, default))
        except ValueError:
            logger.warning(f"环境变量 {key} 格式错误，使用默认值: {default}")
            return default
    
    def _get_bool_env(self, key: str, default: bool = False) -> bool:
        """获取布尔环境变量"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def _get_list_env(self, key: str, default: List[str] = None) -> List[str]:
        """获取列表环境变量（逗号分隔）"""
        if default is None:
            default = []
        
        value = os.getenv(key)
        if not value:
            return default
        
        return [item.strip() for item in value.split(',') if item.strip()]
    
    def _log_config(self):
        """记录配置信息（隐藏敏感信息）"""
        logger.info(f"代理池启用: {self.proxy_enabled}")
        logger.info(f"代理数量: {len(self.proxy_urls)}")
        logger.info(f"Cookie启用: {self.cookie_enabled}")
        logger.info(f"请求头配置: {self.header_profile}")
        logger.info(f"指纹启用: {self.enable_fingerprint}")
        logger.info(f"指纹轮换间隔: {self.header_rotation_interval}")
    
    def create_engine_config(self) -> Dict[str, Any]:
        """创建引擎配置字典"""
        config = {
            'max_connections': int(os.getenv('SCRAPER_MAX_CONNECTIONS', '100')),
            'timeout': int(os.getenv('SCRAPER_TIMEOUT', '15')),
            'max_retries': int(os.getenv('SCRAPER_MAX_RETRIES', '3')),
            'rate_limit': int(os.getenv('SCRAPER_RATE_LIMIT', '10')) if os.getenv('SCRAPER_RATE_LIMIT') else None,
            'enable_cache': os.getenv('SCRAPER_ENABLE_CACHE', 'true').lower() == 'true',
            'cache_ttl': int(os.getenv('SCRAPER_CACHE_TTL', '300')),
            'header_profile': self.header_profile,
            'enable_fingerprint': self.enable_fingerprint,
            'rotation_interval': self.header_rotation_interval,
            'cookie_file': self.cookie_file if self.cookie_enabled else None
        }
        
        # 添加代理配置
        if self.proxy_enabled and self.proxy_urls:
            config['proxy_urls'] = self.proxy_urls
        
        return config


def get_anti_crawler_config() -> AntiCrawlerConfig:
    """获取全局反爬虫配置实例"""
    return AntiCrawlerConfig()


def create_enhanced_engine_from_config() -> EnhancedScraperEngine:
    """根据配置创建增强爬虫引擎"""
    config_loader = get_anti_crawler_config()
    engine_config = config_loader.create_engine_config()
    
    logger.info("根据配置创建增强爬虫引擎")
    return EnhancedScraperEngine(**engine_config)