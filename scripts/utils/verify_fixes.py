#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速验证脚本 - 检查所有修复是否生效
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_service_imports():
    """测试服务模块导入"""
    print("🔍 测试服务模块导入...")
    
    tests = [
        ("services.__init__", "from backend.services import CrawlerService"),
        ("crawler_config_service", "from backend.services.crawler_config_service import CrawlerService"),
        ("crawler_service", "from backend.services.crawler_service import BaseCrawlerService"),
        ("draw_prediction_service", "from backend.services.draw_prediction_service import get_features"),
    ]
    
    failed = []
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"  ✅ {name}")
        except Exception as e:
            print(f"  ❌ {name}: {str(e)[:100]}")
            failed.append((name, str(e)))
    
    return failed

def test_api_route_imports():
    """测试API路由导入"""
    print("\n🔍 测试API路由导入...")
    
    tests = [
        ("crawler", "from backend.api.v1.crawler import router"),
        ("crawler_alert", "from backend.api.v1.crawler_alert import router"),
        ("monitoring_dashboard", "from backend.api.v1.monitoring_dashboard import router"),
        ("draw_prediction", "from backend.api.v1.draw_prediction import router"),
        ("sp_management", "from backend.api.v1.sp_management import router"),
    ]
    
    failed = []
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"  ✅ {name}")
        except Exception as e:
            print(f"  ❌ {name}: {str(e)[:100]}")
            failed.append((name, str(e)))
    
    return failed

def test_create_api_router():
    """测试创建API路由器"""
    print("\n🔍 测试创建API路由器...")
    try:
        from backend.api.v1 import create_api_router
        router = create_api_router()
        print(f"  ✅ API路由器创建成功 ({len(router.routes)} 个路由)")
        return True
    except Exception as e:
        print(f"  ❌ API路由器创建失败: {e}")
        return False

def main():
    print("="*60)
    print("🎯 后端修复验证测试")
    print("="*60)
    
    # 测试服务导入
    failed_services = test_service_imports()
    if failed_services:
        print(f"\n❌ 有 {len(failed_services)} 个服务导入失败")
        for name, error in failed_services:
            print(f"   - {name}: {error}")
        return False
    
    # 测试API路由导入
    failed_routes = test_api_route_imports()
    if failed_routes:
        print(f"\n❌ 有 {len(failed_routes)} 个路由导入失败")
        for name, error in failed_routes:
            print(f"   - {name}: {error}")
        return False
    
    # 测试API路由器
    if not test_create_api_router():
        print("\n❌ API路由器创建失败")
        return False
    
    print("\n" + "="*60)
    print("🎉 所有测试通过！修复应该有效")
    print("="*60)
    print("\n📋 已完成的修复:")
    print("  1. ✅ 修复了 crawler_task_logs 表重复定义")
    print("  2. ✅ 修复了所有 Enum 列的 SQLAlchemy 兼容性")
    print("  3. ✅ 修复了 draw_prediction 导入路径错误")
    print("  4. ✅ 修复了 MetaData.bind 废弃属性问题")
    print("  5. ✅ 修复了 __table_args__ 格式错误")
    print("  6. ✅ 修复了 CrawlerService 导入路径错误")
    print("  7. ✅ 移除了 PostgreSQL 特有类型导入")
    print("\n🚀 现在可以手动启动后端:")
    print("   cd c:\\Users\\11581\\Downloads\\sport-lottery-sweeper")
    print("   .\\start_backend.bat")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
