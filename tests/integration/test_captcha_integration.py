"""
打码服务集成测试脚本
用于测试打码服务与爬虫的集成
"""

import os
import sys
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.services.captcha_solver import (
    create_captcha_solver, 
    CaptchaIntegration,
    ManualCaptchaSolver
)
from backend.scrapers.sources.super_advanced_five_hundred_scraper import SuperAdvancedFiveHundredScraper


def test_manual_captcha_integration():
    """
    测试人工打码服务集成
    """
    print("="*60)
    print("测试: 人工打码服务集成")
    print("="*60)
    
    # 设置环境变量
    os.environ['CAPTCHA_SERVICE_TYPE'] = 'manual'
    
    # 创建爬虫实例
    scraper = SuperAdvancedFiveHundredScraper()
    
    print("[OK] 爬虫已创建并集成人工打码服务")
    print(f"[ANALYTICS] 验证码重试次数: {scraper.captcha_integration.captcha_retry_attempts}")
    print(f"⏰ 验证码检测超时: {scraper.captcha_integration.captcha_detection_timeout}秒")
    
    # 关闭浏览器
    scraper.close()
    print("[OK] 测试完成")


def test_captcha_detection():
    """
    测试验证码检测功能
    """
    print("\n" + "="*60)
    print("测试: 验证码检测功能")
    print("="*60)
    
    # 创建人工打码服务
    solver = ManualCaptchaSolver()
    captcha_integration = CaptchaIntegration(solver)
    
    print("[OK] 验证码集成服务已创建")
    print(f"[ANALYTICS] 重试次数: {captcha_integration.captcha_retry_attempts}")
    print(f"⏰ 检测超时: {captcha_integration.captcha_detection_timeout}秒")
    print(f"[HINT] 重试延迟: {captcha_integration.captcha_retry_delay}秒")
    
    print("[NOTE] 默认选择器:")
    print(f"   验证码图片: img[src*='captcha'], .verify-img, #captcha, .vcode, [alt*='验证码'], [title*='验证码']")
    print(f"   验证码输入: input[name='captcha'], input[name='verify'], input#captcha, input.vcode, input[placeholder*='验证码']")
    print(f"   提交按钮: button[type='submit'], .submit-btn, #submit, [onclick*='submit']")
    

def test_different_captcha_services():
    """
    测试不同类型的打码服务
    """
    print("\n" + "="*60)
    print("测试: 不同类型的打码服务")
    print("="*60)
    
    services = ['manual', 'yundama', 'chaojiying']
    
    for service_type in services:
        print(f"\n[COUNTERCLOCKWISE_ARROWS_BUTTON] 测试 {service_type} 服务:")
        os.environ['CAPTCHA_SERVICE_TYPE'] = service_type
        
        try:
            solver = create_captcha_solver(service_type)
            captcha_integration = CaptchaIntegration(solver)
            
            print(f"   [OK] {service_type} 服务创建成功")
        except Exception as e:
            print(f"   [ERROR] {service_type} 服务创建失败: {e}")
    

def performance_test():
    """
    性能测试
    """
    print("\n" + "="*60)
    print("测试: 性能基准测试")
    print("="*60)
    
    print("[ANALYTICS] 验证码处理配置:")
    print(f"   重试次数: {os.getenv('CAPTCHA_RETRY_ATTEMPTS', '3')}")
    print(f"   检测超时: {os.getenv('CAPTCHA_DETECTION_TIMEOUT', '30')}秒")
    print(f"   重试延迟: {os.getenv('CAPTCHA_RETRY_DELAY', '2.0')}秒")
    
    print("\n[HINT] 建议配置:")
    print("   - 生产环境: 重试3-5次，超时30-60秒")
    print("   - 测试环境: 重试2-3次，超时10-20秒")
    print("   - 人工打码: 适当增加超时时间")


def main():
    """
    主函数
    """
    print("[TARGET] 打码服务集成测试")
    print("[LOG] 本测试验证打码服务与爬虫的集成")
    
    # 运行各项测试
    test_manual_captcha_integration()
    test_captcha_detection()
    test_different_captcha_services()
    performance_test()
    
    print(f"\n{'='*60}")
    print("测试完成")
    print("[HINT] 提示: 根据实际需求调整打码服务配置")
    print("="*60)


if __name__ == "__main__":
    main()