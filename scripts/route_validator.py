#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路由验证工具 - 系统性检查和验证API路由
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

def validate_routes():
    """验证所有API路由是否正确注册"""
    print("🔍 开始路由验证...\n")
    
    # 1. 检查基础导入
    try:
        from backend.api.v1 import router
        print("✅ 成功导入API v1路由器")
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False
    
    # 2. 列出所有路由
    routes = []
    sp_routes = []
    
    for route in router.routes:
        if hasattr(route, 'path'):
            methods = getattr(route, 'methods', set())
            path = getattr(route, 'path', '')
            route_info = {'methods': methods, 'path': path}
            routes.append(route_info)
            
            if '/sp' in path or '/admin/sp' in path:
                sp_routes.append(route_info)
    
    print(f"📊 总路由数量: {len(routes)}")
    print(f"🎯 SP相关路由数量: {len(sp_routes)}\n")
    
    # 3. 检查关键SP路由
    required_sp_routes = [
        '/data-sources',
        '/data-source',
        '/data-source/{source_id}',
        '/data-sources/{source_id}/test',
    ]
    
    print("📋 SP路由检查结果:")
    for req_route in required_sp_routes:
        found = any(req_route in r['path'] for r in sp_routes)
        status = "✅" if found else "❌"
        print(f"  {status} {req_route}")
    
    # 4. 检查路由前缀组合
    print("\n🔗 路由前缀分析:")
    for route in sp_routes:
        path = route['path']
        # 模拟 __init__.py 中的前缀添加
        full_paths = [
            f"/admin/sp{prefix}" if not prefix.startswith('/admin') else prefix 
            for prefix in [path]
        ]
        print(f"  原始: {path}")
        print(f"  完整: {full_paths[0]}")
    
    # 5. 生成路由文档
    print("\n📖 当前可用SP API端点:")
    for route in sp_routes:
        methods = route['methods']
        path = route['path']
        full_path = f"/admin/sp{path}" if not path.startswith('/admin') else path
        print(f"  {methods} {full_path}")
    
    return True

if __name__ == "__main__":
    validate_routes()