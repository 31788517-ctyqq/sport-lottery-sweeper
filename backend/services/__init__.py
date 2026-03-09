"""
服务模块初始化文件 - 仅包含打码服务
"""
from .captcha_solver import (
    CaptchaSolver,
    ManualCaptchaSolver,
    YunDamaCaptchaSolver,
    ChaoJiYingCaptchaSolver,
    CaptchaIntegration,
    get_captcha_solver,
    create_captcha_solver,
    integrate_with_scraper
)

__all__ = [
    'CaptchaSolver',
    'ManualCaptchaSolver',
    'YunDamaCaptchaSolver',
    'ChaoJiYingCaptchaSolver',
    'CaptchaIntegration',
    'get_captcha_solver',
    'create_captcha_solver',
    'integrate_with_scraper'
]

# Services package
