"""
测试admin模块路由注册
"""
import sys
import os
import importlib.util

# 添加项目根目录到Python路径
project_root = os.path.abspath('.')
sys.path.insert(0, project_root)

def test_admin_routes():
    print("开始测试admin模块路由注册...")
    
    # 清除模块缓存
    if 'backend.api.v1.admin' in sys.modules:
        del sys.modules['backend.api.v1.admin']
    
    try:
        import backend.api.v1.admin as admin_module
        print(f"Admin模块导入成功，路由数量: {len(admin_module.router.routes)}")
        
        # 检查是否包含admin-users路由
        admin_users_routes = []
        login_routes = []
        
        for route in admin_module.router.routes:
            if hasattr(route, 'path'):
                if 'admin-users' in route.path:
                    admin_users_routes.append((route.path, getattr(route, 'methods', 'N/A')))
                elif '/login' in route.path and hasattr(route, 'methods'):
                    login_routes.append((route.path, getattr(route, 'methods', 'N/A')))
        
        print(f"找到admin-users路由数量: {len(admin_users_routes)}")
        if admin_users_routes:
            for path, methods in admin_users_routes:
                print(f"  - {path} [{methods}]")
        
        print(f"找到login路由数量: {len(login_routes)}")
        if login_routes:
            for path, methods in login_routes:
                print(f"  - {path} [{methods}]")
        
        # 检查前几个路由
        print("\n前5个路由:")
        for i, route in enumerate(admin_module.router.routes[:5]):
            if hasattr(route, 'path'):
                methods = getattr(route, 'methods', 'N/A')
                print(f"  {i+1}. {route.path} [{methods}]")
        
    except Exception as e:
        print(f"导入admin模块失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_admin_routes()