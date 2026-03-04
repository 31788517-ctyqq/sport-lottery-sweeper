"""
检查FastAPI应用的路由注册情况
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.main import app

def inspect_app_routes():
    print("FastAPI应用路由注册情况:")
    print("="*60)
    
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            print(f"路径: {route.path}")
            print(f"方法: {route.methods}")
            print(f"名称: {getattr(route, 'name', 'N/A')}")
            print("-" * 30)
    
    # 特别检查任务相关的路由
    print("\n任务管理相关路由:")
    task_routes = [r for r in app.routes if '/tasks' in r.path]
    for route in task_routes:
        print(f"路径: {route.path}, 方法: {route.methods}")

if __name__ == "__main__":
    inspect_app_routes()