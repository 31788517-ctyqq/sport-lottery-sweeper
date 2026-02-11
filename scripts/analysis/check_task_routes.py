"""
检查任务管理API路由是否已正确修复
"""
from backend.main import app

def main():
    print("正在检查任务管理API路由...")
    routes_info = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes_info.append({'methods': list(route.methods), 'path': route.path})
    
    # 特别关注任务管理路由
    task_routes = [r for r in routes_info if 'tasks' in r['path'] and ('statistics' in r['path'] or r['path'].endswith('/tasks'))]
    
    print(f"找到 {len(task_routes)} 个任务相关路由:")
    print("-" * 60)
    
    for route in sorted(task_routes, key=lambda x: x['path']):
        print(f"{route['methods']} {route['path']}")
    
    print("-" * 60)
    
    # 检查关键路径是否存在
    expected_paths = [
        '/api/v1/admin/tasks',      # 任务列表
        '/api/v1/admin/tasks/statistics'  # 任务统计
    ]
    
    print("验证关键路径:")
    for expected_path in expected_paths:
        matched = any(expected_path == r['path'] for r in task_routes)
        if matched:
            print(f"✅ {expected_path} - 已找到")
        else:
            print(f"❌ {expected_path} - 未找到")
    
    # 如果主要路径不存在，列出所有任务相关路径
    all_task_routes = [r for r in routes_info if 'tasks' in r['path']]
    if not any('/api/v1/admin/tasks' in r['path'] for r in task_routes):
        print("\n所有任务相关路径:")
        for route in sorted(all_task_routes, key=lambda x: x['path']):
            print(f"  {route['methods']} {route['path']}")

if __name__ == "__main__":
    main()