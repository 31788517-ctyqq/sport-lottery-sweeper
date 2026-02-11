#!/usr/bin/env python3
"""
调试路由注册
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 设置环境变量
os.environ['FULL_API_MODE'] = 'true'

from backend.main import app

print("="*70)
print("🚀 FastAPI路由调试")
print("="*70)
print(f"\n应用名称: {app.title}")
print(f"路由数量: {len(app.routes)}")

print("\n📋 所有路由:")
print("-"*70)

for route in app.routes:
    if hasattr(route, 'path'):
        print(f"{route.path:<50} {route.methods if hasattr(route, 'methods') else 'N/A'}")

print("\n📊 路由统计:")
route_count = {}
for route in app.routes:
    if hasattr(route, 'path') and route.path:
        prefix = route.path.split('/')[1] if route.path.startswith('/') else 'other'
        route_count[prefix] = route_count.get(prefix, 0) + 1

for prefix, count in sorted(route_count.items()):
    print(f"  /{prefix}: {count} 个路由")

print("\n🔍 查找lottery相关路由:")
lottery_routes = [r for r in app.routes if hasattr(r, 'path') and 'lottery' in r.path]
if lottery_routes:
    for route in lottery_routes:
        print(f"  ✓ {route.path}")
else:
    print("  ✗ 未找到lottery路由")

print("\n" + "="*70)
