"""
检查admin路由是否正确注册
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def main():
    print("检查admin路由注册情况...")
    
    # 检查admin_user_management模块是否可以单独导入
    try:
        from backend.api.v1.admin_user_management import router as admin_user_management_router
        print("✓ admin_user_management模块可以导入")
        print(f"  路由数量: {len(admin_user_management_router.routes)}")
        
        for route in admin_user_management_router.routes:
            if hasattr(route, 'path'):
                print(f"  路由路径: {route.path} - 方法: {getattr(route, 'methods', 'N/A')}")
    except Exception as e:
        print(f"✗ 无法导入admin_user_management模块: {e}")
    
    print("\n" + "="*50)
    
    # 检查admin模块
    try:
        from backend.api.v1 import admin
        print("✓ admin模块可以导入")
        
        # 检查admin模块中的路由
        admin_router = admin.router
        print(f"  admin路由数量: {len(admin_router.routes)}")
        
        print("  admin路由中包含用户相关路由:")
        user_routes_found = False
        for route in admin_router.routes:
            if hasattr(route, 'path'):
                if 'user' in route.path.lower():
                    print(f"    找到用户相关路由: {route.path}")
                    user_routes_found = True
                    if hasattr(route, 'methods'):
                        print(f"      方法: {route.methods}")
                elif hasattr(route, 'path') and hasattr(route, 'routes'):
                    # 如果是子路由
                    print(f"    子路由组: {route.path}")
                    for sub_route in route.routes:
                        if hasattr(sub_route, 'path') and 'user' in sub_route.path.lower():
                            print(f"      找到用户相关子路由: {sub_route.path}")
                            user_routes_found = True
                            if hasattr(sub_route, 'methods'):
                                print(f"        方法: {sub_route.methods}")
        
        if not user_routes_found:
            print("    未找到用户相关路由")
    except Exception as e:
        print(f"✗ 无法导入admin模块或检查路由: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()