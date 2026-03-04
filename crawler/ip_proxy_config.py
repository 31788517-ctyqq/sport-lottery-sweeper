"""
IP代理配置模块
用于配置和管理IP代理服务，与爬虫系统集成
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import json
import logging

# AI_WORKING: coder1 @2026-01-27 17:36:34 - 创建IP代理配置模块
@dataclass
class ProxyConfig:
    """
    IP代理配置类
    """
    enabled: bool = True  # 是否启用代理
    provider: str = "89ip"  # 代理提供商
    max_retries: int = 3  # 最大重试次数
    timeout: int = 10  # 请求超时时间
    refresh_interval: int = 300  # 代理池刷新间隔（秒）
    validation_url: str = "http://httpbin.org/ip"  # 验证代理可用性的URL
    min_valid_proxies: int = 5  # 最小有效代理数量
    proxy_usage_threshold: int = 10  # 单个代理最大使用次数

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'ProxyConfig':
        """从字典创建实例"""
        return cls(
            enabled=data.get('enabled', True),
            provider=data.get('provider', '89ip'),
            max_retries=data.get('max_retries', 3),
            timeout=data.get('timeout', 10),
            refresh_interval=data.get('refresh_interval', 300),
            validation_url=data.get('validation_url', 'http://httpbin.org/ip'),
            min_valid_proxies=data.get('min_valid_proxies', 5),
            proxy_usage_threshold=data.get('proxy_usage_threshold', 10)
        )

class IPProxyConfigManager:
    """
    IP代理配置管理器
    用于管理IP代理配置和与爬虫系统的集成
    """
    
    def __init__(self):
        self.config: ProxyConfig = ProxyConfig()
        self.logger = logging.getLogger(__name__)
    
    def load_config(self, config_path: str) -> bool:
        """
        从文件加载配置
        :param config_path: 配置文件路径
        :return: 是否加载成功
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.config = ProxyConfig.from_dict(data)
                self.logger.info(f"从 {config_path} 加载代理配置成功")
                return True
        except FileNotFoundError:
            self.logger.warning(f"配置文件 {config_path} 不存在，使用默认配置")
            return False
        except Exception as e:
            self.logger.error(f"加载配置文件 {config_path} 失败: {str(e)}")
            return False
    
    def save_config(self, config_path: str) -> bool:
        """
        保存配置到文件
        :param config_path: 配置文件路径
        :return: 是否保存成功
        """
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, ensure_ascii=False, indent=2)
            self.logger.info(f"代理配置已保存到 {config_path}")
            return True
        except Exception as e:
            self.logger.error(f"保存配置文件 {config_path} 失败: {str(e)}")
            return False
    
    def get_proxy_config(self) -> ProxyConfig:
        """获取当前代理配置"""
        return self.config
    
    def update_config(self, **kwargs) -> bool:
        """
        更新配置
        :param kwargs: 配置参数
        :return: 是否更新成功
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                else:
                    self.logger.warning(f"配置项 {key} 不存在")
            return True
        except Exception as e:
            self.logger.error(f"更新配置失败: {str(e)}")
            return False
    
    def get_crawler_headers(self) -> Dict[str, str]:
        """
        获取爬虫请求头
        :return: 请求头字典
        """
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def get_enhanced_crawler_config(self) -> Dict:
        """
        获取增强版爬虫配置（包含代理设置）
        :return: 爬虫配置字典
        """
        return {
            'use_proxy': self.config.enabled,
            'proxy_provider': self.config.provider,
            'max_retries': self.config.max_retries,
            'timeout': self.config.timeout,
            'headers': self.get_crawler_headers(),
            'validation_url': self.config.validation_url,
            'min_valid_proxies': self.config.min_valid_proxies,
            'proxy_usage_threshold': self.config.proxy_usage_threshold
        }

# AI_DONE: coder1 @2026-01-27 17:36:34