"""
打码服务演示脚本
展示如何配置和使用不同的打码服务
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.services.captcha_solver import (
    create_captcha_solver, 
    CaptchaIntegration,
    ManualCaptchaSolver,
    YunDamaCaptchaSolver,
    ChaoJiYingCaptchaSolver
)
from backend.scrapers.sources.super_advanced_five_hundred_scraper import SuperAdvancedFiveHundredScraper


def demo_manual_captcha_service():
    """
    演示人工打码服务
    """
    print("\n" + "="*60)
    print("演示: 人工打码服务")
    print("="*60)
    
    # 设置环境变量
    os.environ['CAPTCHA_SERVICE_TYPE'] = 'manual'
    
    # 创建打码服务
    solver = create_captcha_solver('manual')
    captcha_integration = CaptchaIntegration(solver)
    
    print("✅ 人工打码服务已准备就绪")
    print("📝 使用方法:")
    print("   - 当遇到验证码时，将在控制台显示验证码URL")
    print("   - 用户需手动访问URL查看验证码")
    print("   - 在控制台输入验证码内容")
    print("   - 程序将自动填入并提交")


def demo_yundama_service():
    """
    演示云打码服务
    """
    print("\n" + "="*60)
    print("演示: 云打码服务")
    print("="*60)
    
    # 设置环境变量（需要替换为真实账号信息）
    os.environ['CAPTCHA_SERVICE_TYPE'] = 'yundama'
    os.environ['YUNDAMA_USERNAME'] = 'your_username_here'
    os.environ['YUNDAMA_PASSWORD'] = 'your_password_here'
    os.environ['YUNDAMA_APP_ID'] = 'your_app_id_here'
    os.environ['YUNDAMA_APP_KEY'] = 'your_app_key_here'
    
    try:
        solver = create_captcha_solver('yundama')
        captcha_integration = CaptchaIntegration(solver)
        
        print("✅ 云打码服务已配置")
        print("📝 配置要点:")
        print("   - 需要在环境变量中设置YUNDAMA相关参数")
        print("   - 支持多种验证码类型")
        print("   - 自动识别并返回结果")
        print("   - 适用于大批量验证码处理")
        
    except Exception as e:
        print(f"⚠️  云打码服务配置失败: {e}")
        print("💡 请确保已注册云打码账号并充值")


def demo_chaojiying_service():
    """
    演示超级鹰服务
    """
    print("\n" + "="*60)
    print("演示: 超级鹰服务")
    print("="*60)
    
    # 设置环境变量（需要替换为真实账号信息）
    os.environ['CAPTCHA_SERVICE_TYPE'] = 'chaojiying'
    os.environ['CHAOJIYING_USERNAME'] = 'your_username_here'
    os.environ['CHAOJIYING_PASSWORD'] = 'your_password_here'
    os.environ['CHAOJIYING_SOFT_ID'] = 'your_soft_id_here'
    os.environ['CHAOJIYING_KIND'] = '1004'  # 验证码类型
    
    try:
        solver = create_captcha_solver('chaojiying')
        captcha_integration = CaptchaIntegration(solver)
        
        print("✅ 超级鹰服务已配置")
        print("📝 配置要点:")
        print("   - 需要在环境变量中设置CHAOJIYING相关参数")
        print("   - 支持超过200种验证码类型")
        print("   - 识别准确率高，速度快")
        print("   - 提供详细的API文档")
        
    except Exception as e:
        print(f"⚠️  超级鹰服务配置失败: {e}")
        print("💡 请确保已注册超级鹰账号并充值")


def demo_integration_with_scraper():
    """
    演示与爬虫的集成
    """
    print("\n" + "="*60)
    print("演示: 与爬虫集成")
    print("="*60)
    
    # 设置为人工打码服务
    os.environ['CAPTCHA_SERVICE_TYPE'] = 'manual'
    
    print("🔧 正在初始化爬虫...")
    scraper = SuperAdvancedFiveHundredScraper()
    
    print("✅ 爬虫已集成打码服务")
    print("📝 集成特性:")
    print("   - 自动检测页面验证码元素")
    print("   - 智能选择验证码处理策略")
    print("   - 失败后自动重试机制")
    print("   - 支持多种验证码类型")
    
    # 关闭浏览器
    scraper.close()


def show_configuration_examples():
    """
    显示配置示例
    """
    print("\n" + "="*60)
    print("配置示例")
    print("="*60)
    
    print("# .env 文件配置示例:")
    print("""
# 启用打码服务
CAPTCHA_ENABLED=true
CAPTCHA_SERVICE_TYPE=manual  # 可选: manual, yundama, chaojiying

# 云打码服务配置
YUNDAMA_USERNAME=your_username
YUNDAMA_PASSWORD=your_password
YUNDAMA_APP_ID=your_app_id
YUNDAMA_APP_KEY=your_app_key

# 超级鹰服务配置
CHAOJIYING_USERNAME=your_username
CHAOJIYING_PASSWORD=your_password
CHAOJIYING_SOFT_ID=your_soft_id
CHAOJIYING_KIND=1004  # 验证码类型

# 验证码处理配置
CAPTCHA_DETECTION_TIMEOUT=30
CAPTCHA_RETRY_ATTEMPTS=3
CAPTCHA_RETRY_DELAY=2.0
    """.strip())
    
    print("\n# Python代码配置示例:")
    print("""
# 创建特定类型的打码服务
from backend.services.captcha_solver import create_captcha_solver, CaptchaIntegration

# 人工打码
solver = create_captcha_solver('manual')
captcha_integration = CaptchaIntegration(solver)

# 云打码
solver = create_captcha_solver('yundama')
captcha_integration = CaptchaIntegration(solver)

# 超级鹰
solver = create_captcha_solver('chaojiying')
captcha_integration = CaptchaIntegration(solver)
    """.strip())


def main():
    """
    主函数
    """
    print("🎯 打码服务集成演示")
    print("📋 本演示展示如何在爬虫项目中集成打码服务")
    
    # 演示不同打码服务
    demo_manual_captcha_service()
    demo_yundama_service()
    demo_chaojiying_service()
    
    # 演示与爬虫集成
    demo_integration_with_scraper()
    
    # 显示配置示例
    show_configuration_examples()
    
    print("\n" + "="*60)
    print("演示完成")
    print("💡 提示: 根据实际需求选择合适的打码服务")
    print("="*60)


if __name__ == "__main__":
    main()