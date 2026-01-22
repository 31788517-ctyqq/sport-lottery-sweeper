#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试合并后的路由注册功能
"""
import sys
import os
import logging

# 设置Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

print("=" * 60)
print("开始测试合并后的路由注册")
print("=" * 60)

try:
    # 导入路由创建函数
    from backend.api.v1 import create_api_router
    print("✅ 成功导入 create_api_router 函数")
    
    # 创建路由器
    router = create_api_router()
    print(f"✅ 路由器创建成功，总共注册了 {len(router.routes)} 个路由")
    
    # 显示所有注册的路由
    print("\n📋 注册的路由列表:")
    route_count = 0
    for route in router.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ', '.join(route.methods)
            print(f"  {route_count+1:2d}. [{methods}] {route.path}")
            route_count += 1
    
    print(f"\n🎯 总计: {route_count} 个有效路由")
    
    # 检查特定路由是否存在
    expected_routes = [
        '/admin',
        '/auth',
        '/auth/login',
        '/auth/me', 
        '/intelligence',
        '/data-submission',
        '/admin-users',
        '/frontend-users',
        '/lottery',
        '/matches',
        '/public-matches'
    ]
    
    print("\n🔍 检查关键路由:")
    missing_routes = []
    for expected_route in expected_routes:
        found = False
        for route in router.routes:
            if hasattr(route, 'path') and expected_route in route.path:
                found = True
                break
        if found:
            print(f"  ✅ {expected_route}")
        else:
            print(f"  ❌ {expected_route} (未找到)")
            missing_routes.append(expected_route)
    
    if missing_routes:
        print(f"\n⚠️  缺失的关键路由: {missing_routes}")
    else:
        print("\n🎉 所有关键路由都已成功注册!")
        
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ 运行时错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
