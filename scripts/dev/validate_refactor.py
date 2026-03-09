"""
重构验证脚本
用于验证项目结构是否已成功重构为现代化布局
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

def test_directory_structure():
    """测试目录结构是否符合预期"""
    print("\n正在验证目录结构...")
    
    expected_paths = [
        "src/backend/main.py",
        "src/backend/config.py",
        "src/backend/database.py",
        "src/backend/api/__init__.py",
        "src/backend/scrapers/__init__.py",
        "src/backend/scrapers/zqszsc_scraper.py",
        "src/shared/models.py",
        "src/shared/utils.py",
        "config/dev/settings.toml",
        "config/prod/settings.toml",
        "docker/docker-compose.yml",
        "frontend/",
        "tests/backend/unit/",
        "scripts/dev/test_startup.py",
        "pyproject.toml",
        "README.md"
    ]
    
    base_path = Path(__file__).resolve().parent.parent.parent
    
    all_exist = True
    for path_str in expected_paths:
        path = base_path / path_str.rstrip('/')
        is_dir = path_str.endswith('/')
        exists = path.is_dir() if is_dir else path.is_file()
        
        if exists:
            print(f"✓ 存在: {path_str}")
        else:
            print(f"✗ 缺失: {path_str}")
            all_exist = False
    
    if all_exist:
        print("\n✓ 目录结构验证通过！")
    else:
        print("\n✗ 目录结构存在问题")
    
    return all_exist

def display_project_structure():
    """显示当前项目结构概览"""
    print("\n项目结构概览:")
    print("""
sport-lottery-sweeper/
├── .github/
├── config/                 # 统一配置目录
│   ├── dev/
│   └── prod/
├── docker/                 # 集中管理Docker资源
├── docs/                   # 文档集中管理
├── scripts/                # 可执行脚本
├── src/                    # 核心源代码
│   ├── backend/            # 后端应用
│   │   ├── api/            # API路由
│   │   ├── scrapers/       # 爬虫模块
│   │   ├── cache/          # 缓存管理
│   │   └── ...             # 其他后端模块
│   └── shared/             # 共享代码
│       ├── models.py       # 数据模型
│       └── utils.py        # 工具函数
├── frontend/               # 前端保持独立结构
├── tests/                  # 分层测试目录
├── .env.example
├── pyproject.toml          # 统一依赖管理
├── Makefile
└── README.md
    """)

def main():
    """主验证函数"""
    print("=" * 60)
    print("竞彩足球扫盘系统 - 重构验证")
    print("=" * 60)
    
    # 显示项目结构概览
    display_project_structure()
    
    # 验证目录结构
    if not test_directory_structure():
        print("\n❌ 重构失败：目录结构不符合预期")
        return False
    
    # 测试模块导入
    if not test_imports():
        print("\n❌ 重构失败：模块导入存在问题")
        return False
    
    # 测试配置加载
    if not test_config():
        print("\n❌ 重构失败：配置加载存在问题")
        return False
    
    print("\n✅ 重构验证全部通过！")
    print("项目已成功重构为现代化布局，具有更好的模块化和可维护性")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)