"""
测试admin模块导入
"""
import sys
from pathlib import Path
import logging

# 设置日志级别为DEBUG以查看详细信息
logging.basicConfig(level=logging.DEBUG)

def main():
    # 添加项目根目录到Python路径
    project_root = Path(__file__).resolve().parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    print("开始测试admin模块导入...")
    
    # 首先测试各个模块是否可以单独导入
    modules_to_test = [
        ('backend.api.v1.users', 'router'),
        ('backend.api.v1.admin_user_management', 'router'),
        ('backend.api.v1.frontend_user_management', 'router'),
        ('backend.api.v1.simple_user_api', 'router'),
        ('backend.api.v1.sp_management', 'router'),
        ('backend.api.v1.draw_prediction', 'router'),
        ('backend.api.v1.hedging', 'router'),
        ('backend.api.v1.intelligence', 'router'),
        ('backend.api.v1.match_admin', 'router'),
        ('backend.api.v1.monitoring_dashboard', 'router'),
    ]
    
    for module_path, obj_name in modules_to_test:
        try:
            module = __import__(module_path, fromlist=[obj_name])
            router = getattr(module, obj_name)
            print(f"✓ {module_path} imported successfully, routes: {len(router.routes)}")
        except Exception as e:
            print(f"✗ {module_path} import failed: {e}")
            import traceback
            traceback.print_exc()
    
    # 测试admin模块导入
    print("\n测试admin模块导入...")
    try:
        import backend.api.v1.admin
        print("✓ admin模块导入成功")
        
        # 检查admin模块中是否有我们添加的路由
        admin_router = backend.api.v1.admin.router
        print(f"admin路由数量: {len(admin_router.routes)}")
        
        # 检查是否包含admin-users路由
        admin_users_routes = []
        login_routes = []
        
        for route in admin_router.routes:
            if hasattr(route, 'path'):
                if 'admin-users' in route.path:
                    admin_users_routes.append(route.path)
                elif '/login' in route.path and 'admin' in route.path:
                    login_routes.append(route.path)
        
        print(f"admin-users路由: {len(admin_users_routes)} 个")
        print(f"admin login路由: {len(login_routes)} 个")
        
        if admin_users_routes:
            print("  - ", "\n  - ".join(admin_users_routes))
        if login_routes:
            print("  - ", "\n  - ".join(login_routes))
            
    except Exception as e:
        print(f"✗ admin模块导入失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()