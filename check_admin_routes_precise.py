"""
更精确地检查admin路由注册情况
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def check_admin_router_structure():
    print("检查admin模块路由结构...")
    
    try:
        from backend.api.v1 import admin
        router = admin.router
        
        print(f"Admin路由总数: {len(router.routes)}")
        
        # 查找所有路由
        for i, route in enumerate(router.routes):
            if hasattr(route, 'path'):
                print(f"{i+1:2d}. 路径: {route.path}")
                if hasattr(route, 'methods'):
                    print(f"     方法: {route.methods}")
                if hasattr(route, 'name'):
                    print(f"     名称: {getattr(route, 'name', 'N/A')}")
                
                # 检查是否为子路由器
                if hasattr(route, 'routes'):
                    print(f"     [子路由器 - 包含 {len(route.routes)} 个子路由]")
                    for j, sub_route in enumerate(route.routes):
                        if hasattr(sub_route, 'path'):
                            print(f"         {j+1}. 子路径: {route.path}{sub_route.path}")
                            if hasattr(sub_route, 'methods'):
                                print(f"             方法: {sub_route.methods}")
                            if hasattr(sub_route, 'name'):
                                print(f"             名称: {getattr(sub_route, 'name', 'N/A')}")
                print()
        
        print("="*60)
        
        # 特别搜索包含admin-users的路由
        print("搜索包含'admin-users'的路由:")
        found_admin_users = False
        for route in router.routes:
            if 'admin-users' in route.path:
                print(f"  找到: {route.path}")
                found_admin_users = True
            elif hasattr(route, 'routes'):
                # 检查子路由
                for sub_route in route.routes:
                    if hasattr(sub_route, 'path') and 'admin-users' in f"{route.path}{sub_route.path}":
                        print(f"  找到子路由: {route.path}{sub_route.path}")
                        found_admin_users = True
        
        if not found_admin_users:
            print("  未找到包含'admin-users'的路由")
        
        print("\n搜索包含'login'的路由:")
        found_login = False
        for route in router.routes:
            if 'login' in route.path.lower():
                print(f"  找到: {route.path}")
                found_login = True
            elif hasattr(route, 'routes'):
                # 检查子路由
                for sub_route in route.routes:
                    if hasattr(sub_route, 'path') and 'login' in f"{sub_route.path}".lower():
                        print(f"  找到子路由: {route.path}{sub_route.path}")
                        found_login = True
        
        if not found_login:
            print("  未找到包含'login'的路由")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

def main():
    check_admin_router_structure()

if __name__ == "__main__":
    main()