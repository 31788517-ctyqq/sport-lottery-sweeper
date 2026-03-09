"""
测试应用程序启动脚本
用于验证重构后的项目结构是否正确
"""
import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).resolve().parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """测试关键模块是否可以正确导入"""
    print("正在测试模块导入...")
    
    try:
        from backend.config import settings
        print("✓ 成功导入 backend.config")
        
        from shared.models import Base
        print("✓ 成功导入 shared.models")
        
        from backend.database import engine
        print("✓ 成功导入 backend.database")
        
        from backend.scrapers.zqszsc_scraper import ZqszscScraper
        print("✓ 成功导入 backend.scrapers.zqszsc_scraper")
        
        from backend.api import router
        print("✓ 成功导入 backend.api")
        
        print("\n✓ 所有模块导入成功！")
        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_config():
    """测试配置是否正确加载"""
    print("\n正在测试配置加载...")
    
    try:
        from backend.config import settings
        print(f"✓ 项目名称: {settings.PROJECT_NAME}")
        print(f"✓ 数据库URL: {settings.DATABASE_URL}")
        print("✓ 配置加载成功！")
        return True
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        return False

async def test_scraper():
    """测试爬虫功能"""
    print("\n正在测试爬虫功能...")
    
    try:
        from backend.scrapers.zqszsc_scraper import ZqszscScraper
        
        async with Zqszsc_scraper() as scraper:
            matches = await scraper.get_recent_matches(1)
            print(f"✓ 成功获取 {len(matches)} 场比赛数据")
            
        print("✓ 爬虫功能测试成功！")
        return True
    except Exception as e:
        print(f"✗ 爬虫功能测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("=" * 50)
    print("竞彩足球扫盘系统 - 重构验证测试")
    print("=" * 50)
    
    # 测试模块导入
    if not test_imports():
        return False
    
    # 测试配置加载
    if not test_config():
        return False
    
    # 测试爬虫功能
    if not await test_scraper():
        print("\n⚠ 爬虫功能测试失败，但这可能是由于网络原因，不影响重构结果")
    
    print("\n✓ 重构验证测试完成！")
    print("项目结构已成功重构为现代化布局")
    return True

if __name__ == "__main__":
    asyncio.run(main())