"""
打码服务配置文件
定义打码服务的各种配置选项
"""

import os
from typing import Dict, Any, Optional


class CaptchaConfig:
    """
    打码服务配置类
    """
    
    # 验证码类型映射
    CAPTCHA_TYPES = {
        'image': '图片验证码',
        'slider': '滑块验证码',
        'click': '点击验证码',
        'math': '数学验证码'
    }
    
    # 支持的打码服务商
    SUPPORTED_SERVICES = {
        'manual': {
            'name': '人工打码',
            'description': '通过人工输入解决验证码',
            'requires_auth': False
        },
        'yundama': {
            'name': '云打码',
            'description': '使用云打码API自动解决验证码',
            'requires_auth': True
        },
        'chaojiying': {
            'name': '超级鹰',
            'description': '使用超级鹰API自动解决验证码',
            'requires_auth': True
        },
        'tencent_captcha': {
            'name': '腾讯验证码',
            'description': '使用腾讯验证码防护',
            'requires_auth': True
        }
    }
    
    def __init__(self):
        # 从环境变量或默认值加载配置
        self.service_type = os.getenv('CAPTCHA_SERVICE_TYPE', 'manual')
        self.enabled = os.getenv('CAPTCHA_ENABLED', 'true').lower() == 'true'
        
        # 云打码配置
        self.yundama_username = os.getenv('YUNDAMA_USERNAME', '')
        self.yundama_password = os.getenv('YUNDAMA_PASSWORD', '')
        self.yundama_app_id = os.getenv('YUNDAMA_APP_ID', '')
        self.yundama_app_key = os.getenv('YUNDAMA_APP_KEY', '')
        
        # 超级鹰配置
        self.chaojiying_username = os.getenv('CHAOJIYING_USERNAME', '')
        self.chaojiying_password = os.getenv('CHAOJIYING_PASSWORD', '')
        self.chaojiying_soft_id = os.getenv('CHAOJIYING_SOFT_ID', '')
        self.chaojiying_kind = os.getenv('CHAOJIYING_KIND', '1004')  # 验证码类型
        
        # 腾讯验证码配置
        self.tencent_captcha_app_id = os.getenv('TENCENT_CAPTCHA_APP_ID', '')
        self.tencent_captcha_app_secret = os.getenv('TENCENT_CAPTCHA_APP_SECRET', '')
        
        # 验证码检测配置
        self.captcha_detection_timeout = int(os.getenv('CAPTCHA_DETECTION_TIMEOUT', '30'))
        self.captcha_retry_attempts = int(os.getenv('CAPTCHA_RETRY_ATTEMPTS', '3'))
        self.captcha_retry_delay = float(os.getenv('CAPTCHA_RETRY_DELAY', '2.0'))
        
        # 验证配置
        self.validate_config()
    
    def validate_config(self) -> bool:
        """
        验证配置是否正确
        :return: 配置是否有效
        """
        if self.service_type not in self.SUPPORTED_SERVICES:
            raise ValueError(f"不支持的打码服务类型: {self.service_type}")
        
        if self.service_type != 'manual':
            # 检查需要认证的服务是否提供了认证信息
            service_info = self.SUPPORTED_SERVICES[self.service_type]
            if service_info['requires_auth']:
                auth_fields = self._get_required_auth_fields()
                for field in auth_fields:
                    if not getattr(self, field):
                        raise ValueError(f"打码服务 {self.service_type} 需要配置 {field}")
        
        return True
    
    def _get_required_auth_fields(self) -> list:
        """
        获取当前服务类型所需的认证字段
        :return: 认证字段列表
        """
        if self.service_type == 'yundama':
            return ['yundama_username', 'yundama_password']
        elif self.service_type == 'chaojiying':
            return ['chaojiying_username', 'chaojiying_password', 'chaojiying_soft_id']
        elif self.service_type == 'tencent_captcha':
            return ['tencent_captcha_app_id', 'tencent_captcha_app_secret']
        return []
    
    def get_service_config(self) -> Dict[str, Any]:
        """
        获取当前服务的配置
        :return: 服务配置字典
        """
        if self.service_type == 'yundama':
            return {
                'username': self.yundama_username,
                'password': self.yundama_password,
                'app_id': self.yundama_app_id,
                'app_key': self.yundama_app_key
            }
        elif self.service_type == 'chaojiying':
            return {
                'username': self.chaojiying_username,
                'password': self.chaojiying_password,
                'soft_id': self.chaojiying_soft_id,
                'kind': self.chaojiying_kind
            }
        elif self.service_type == 'tencent_captcha':
            return {
                'app_id': self.tencent_captcha_app_id,
                'app_secret': self.tencent_captcha_app_secret
            }
        
        return {}
    
    def is_service_available(self) -> bool:
        """
        检查打码服务是否可用
        :return: 服务是否可用
        """
        if not self.enabled:
            return False
        
        if self.service_type == 'manual':
            return True  # 人工打码始终可用
        
        # 检查认证信息是否完整
        try:
            self.validate_config()
            return True
        except ValueError:
            return False
    
    def get_captcha_selectors(self) -> Dict[str, str]:
        """
        获取常见的验证码元素选择器
        :return: 选择器字典
        """
        return {
            'captcha_img': 'img[src*="captcha"], .verify-img, #captcha, .vcode, [alt*="验证码"], [title*="验证码"]',
            'captcha_input': 'input[name="captcha"], input[name="verify"], input#captcha, input.vcode, input[placeholder*="验证码"]',
            'submit_btn': 'button[type="submit"], .submit-btn, #submit, [onclick*="submit"]',
            'verify_btn': '.verify-btn, #verify, button.verify, [onclick*="verify"]'
        }


# 全局配置实例
captcha_config = CaptchaConfig()


def get_captcha_config() -> CaptchaConfig:
    """
    获取打码服务配置实例
    :return: 配置实例
    """
    return captcha_config


def update_config_from_dict(config_dict: Dict[str, Any]) -> None:
    """
    从字典更新配置
    :param config_dict: 配置字典
    """
    for key, value in config_dict.items():
        if hasattr(captcha_config, key):
            setattr(captcha_config, key, value)


if __name__ == "__main__":
    # 测试配置
    config = get_captcha_config()
    print(f"当前打码服务类型: {config.service_type}")
    print(f"服务是否启用: {config.enabled}")
    print(f"支持的服务: {list(config.SUPPORTED_SERVICES.keys())}")
    print(f"验证码选择器: {config.get_captcha_selectors()}")