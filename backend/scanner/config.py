"""
扫描器配置模块
管理扫描参数和设置
"""
import os
from pathlib import Path
from typing import Dict, List, Set, Optional
import yaml


class ScanConfig:
    """扫描配置类"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        "scan": {
            "backend_dir": "backend",
            "api_dirs": ["api/v1"],
            "output_dir": "reports",
            "report_format": ["json", "md", "csv"],
            "generate_tests": True,
            "test_output_dir": "generated_tests",
        },
        "auth": {
            "sensitive_patterns": [
                r"/users?/.*",
                r"/profile.*",
                r"/admin.*",
                r"/data.*",
                r"/config.*",
                r"/settings.*",
                r"/payment.*",
                r"/wallet.*",
                r"/balance.*",
                r"/transaction.*",
            ],
            "public_patterns": [
                r"/auth/login.*",
                r"/auth/register.*",
                r"/public/.*",
                r"/health.*",
                r"/docs.*",
                r"/openapi\.json",
            ],
            "admin_patterns": [
                r"/admin/.*",
                r"/users/admin.*",
                r"/system/.*",
                r"/config/.*",
                r"/settings/.*",
            ],
        },
        "validation": {
            "sensitive_params": [
                "password",
                "token",
                "secret",
                "key",
                "credit_card",
                "ssn",
                "phone",
                "email",
            ],
            "common_params_requiring_validation": [
                "id",
                "user_id",
                "page",
                "size",
                "limit",
                "offset",
            ],
            "data_creation_patterns": [
                r"/create.*",
                r"/register.*",
                r"/add.*",
                r"/insert.*",
                r"/new.*",
                r"/save.*",
            ],
        },
        "routes": {
            "expected_patterns": [
                "/api/v1/health",
                "/api/v1/info",
                "/api/v1/users/profile",
                "/api/v1/admin/users",
                "/api/v1/auth/login",
                "/api/v1/auth/register",
            ],
        },
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置
        
        Args:
            config_file: 配置文件路径（可选）
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_file and Path(config_file).exists():
            self.load_config(config_file)
    
    def load_config(self, config_file: str) -> None:
        """
        从文件加载配置
        
        Args:
            config_file: 配置文件路径
        """
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                loaded_config = yaml.safe_load(f)
            
            # 深度合并配置
            self._merge_config(self.config, loaded_config)
            
        except Exception as e:
            raise ValueError(f"加载配置文件失败: {e}")
    
    def _merge_config(self, base: Dict, override: Dict) -> None:
        """
        深度合并配置
        
        Args:
            base: 基础配置
            override: 覆盖配置
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def save_config(self, config_file: str) -> None:
        """
        保存配置到文件
        
        Args:
            config_file: 配置文件路径
        """
        try:
            config_dir = Path(config_file).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
        
        except Exception as e:
            raise ValueError(f"保存配置文件失败: {e}")
    
    @property
    def backend_dir(self) -> str:
        """获取backend目录路径"""
        return self.config["scan"]["backend_dir"]
    
    @property
    def api_dirs(self) -> List[str]:
        """获取API目录列表"""
        return self.config["scan"]["api_dirs"]
    
    @property
    def output_dir(self) -> str:
        """获取输出目录路径"""
        return self.config["scan"]["output_dir"]
    
    @property
    def report_formats(self) -> List[str]:
        """获取报告格式列表"""
        return self.config["scan"]["report_format"]
    
    @property
    def generate_tests(self) -> bool:
        """获取是否生成测试"""
        return self.config["scan"]["generate_tests"]
    
    @property
    def test_output_dir(self) -> str:
        """获取测试输出目录"""
        return self.config["scan"]["test_output_dir"]
    
    def get_sensitive_patterns(self) -> List[str]:
        """获取敏感接口模式"""
        return self.config["auth"]["sensitive_patterns"]
    
    def get_public_patterns(self) -> List[str]:
        """获取公共接口模式"""
        return self.config["auth"]["public_patterns"]
    
    def get_admin_patterns(self) -> List[str]:
        """获取管理员接口模式"""
        return self.config["auth"]["admin_patterns"]
    
    def get_sensitive_params(self) -> List[str]:
        """获取敏感参数列表"""
        return self.config["validation"]["sensitive_params"]
    
    def get_common_params_requiring_validation(self) -> List[str]:
        """获取需要验证的常见参数"""
        return self.config["validation"]["common_params_requiring_validation"]
    
    def get_data_creation_patterns(self) -> List[str]:
        """获取数据创建接口模式"""
        return self.config["validation"]["data_creation_patterns"]
    
    def get_expected_route_patterns(self) -> List[str]:
        """获取预期路由模式"""
        return self.config["routes"]["expected_patterns"]
    
    def update_setting(self, section: str, key: str, value: any) -> None:
        """
        更新配置设置
        
        Args:
            section: 配置部分
            key: 配置键
            value: 配置值
        """
        if section in self.config and key in self.config[section]:
            self.config[section][key] = value
        else:
            raise KeyError(f"配置项不存在: {section}.{key}")
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return self.config.copy()


# 全局配置实例
_config_instance: Optional[ScanConfig] = None


def get_config(config_file: Optional[str] = None) -> ScanConfig:
    """
    获取配置实例（单例模式）
    
    Args:
        config_file: 配置文件路径（可选）
        
    Returns:
        ScanConfig: 配置实例
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = ScanConfig(config_file)
    
    return _config_instance


def reset_config() -> None:
    """重置配置实例"""
    global _config_instance
    _config_instance = None


# 创建默认配置文件
def create_default_config(config_file: str = "scanner_config.yaml") -> str:
    """
    创建默认配置文件
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        str: 配置文件路径
    """
    config = ScanConfig()
    config.save_config(config_file)
    return config_file