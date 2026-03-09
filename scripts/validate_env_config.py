#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境配置验证脚本
用于验证项目环境配置是否正确
"""

import os
import sys
from pathlib import Path
import subprocess
from typing import Dict, List, Tuple


def check_python_version():
    """检查Python版本"""
    major, minor, *_ = sys.version_info
    if major < 3 or (major == 3 and minor < 11):
        print(f"❌ 错误: Python版本过低，需要Python 3.11+，当前版本: {major}.{minor}")
        return False
    else:
        print(f"✅ Python版本检查通过: {major}.{minor}")
        return True


def check_required_packages():
    """检查必需的包是否已安装"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "alembic",
        "psycopg2-binary",
        "redis",
        "celery",
        "requests",
        "numpy",
        "pandas",
        "playwright",
        "beautifulsoup4",
        "python-dotenv",
        "pydantic",
        "pytest",
        "pytest-asyncio",
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少必需的包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    else:
        print("✅ 所有必需包均已安装")
        return True


def check_env_vars():
    """检查必需的环境变量"""
    required_vars = [
        "DATABASE_URL",
        "REDIS_URL",
        "SECRET_KEY",
        "ALGORITHM",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "ADMIN_USERNAME",
        "ADMIN_PASSWORD",
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少必需的环境变量: {', '.join(missing_vars)}")
        print("请检查 .env 文件配置")
        return False
    else:
        print("✅ 所有必需环境变量均已设置")
        return True


def check_directories():
    """检查必需的目录是否存在"""
    required_dirs = [
        "backend",
        "frontend",
        "logs",
        "uploads",
        "data",
        "storage",
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"❌ 缺少必需的目录: {', '.join(missing_dirs)}")
        print("部分功能可能无法正常工作")
        return False
    else:
        print("✅ 所有必需目录均已存在")
        return True


def check_database_connection():
    """尝试连接数据库"""
    try:
        import sqlalchemy
        from sqlalchemy import create_engine
        
        database_url = os.getenv("DATABASE_URL", "")
        if not database_url:
            print("⚠️  未设置数据库URL，跳过数据库连接测试")
            return True
            
        engine = create_engine(database_url)
        connection = engine.connect()
        connection.close()
        print("✅ 数据库连接测试通过")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False


def check_frontend_dependencies():
    """检查前端依赖"""
    try:
        result = subprocess.run(
            ["node", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode != 0:
            print("❌ Node.js 未安装或不可用")
            return False
        else:
            print(f"✅ Node.js 版本检查通过: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Node.js 未安装或不在PATH中")
        return False
    
    try:
        result = subprocess.run(
            ["pnpm", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode != 0:
            print("⚠️  pnpm 未安装或不可用，将尝试使用npm")
        else:
            print(f"✅ pnpm 版本检查通过: {result.stdout.strip()}")
    except FileNotFoundError:
        print("⚠️  pnpm 未安装或不在PATH中，将尝试使用npm")
    
    return True


def run_comprehensive_check():
    """运行综合检查"""
    print("=" * 60)
    print("体育彩票扫盘系统 - 环境配置验证")
    print("=" * 60)
    
    checks = [
        ("Python版本", check_python_version),
        ("必需包", check_required_packages),
        ("环境变量", check_env_vars),
        ("必需目录", check_directories),
        ("数据库连接", check_database_connection),
        ("前端依赖", check_frontend_dependencies),
    ]
    
    results = []
    for name, func in checks:
        print(f"\n🔍 检查{name}...")
        result = func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("检查结果汇总:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总览: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("\n🎉 所有检查均已通过！系统环境配置正确。")
        return True
    else:
        print(f"\n⚠️  {total - passed} 项检查未通过，请根据上述信息修复问题。")
        return False


if __name__ == "__main__":
    success = run_comprehensive_check()
    sys.exit(0 if success else 1)