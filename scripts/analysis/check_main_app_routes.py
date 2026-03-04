import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def main():
    try:
        from backend.main import app

        print('=== 检查整个应用的路由 ===')
        user_routes_found = False
        login_routes_found = False

        for route in app.routes:
            if hasattr(route, 'path'):
                if 'admin-users' in route.path:
                    print(f'FOUND ADMIN-USERS ROUTE: {route.path}')
                    user_routes_found = True
                elif '/login' in route.path and 'admin' in route.path:
                    print(f'FOUND ADMIN LOGIN ROUTE: {route.path}')
                    login_routes_found = True
                elif hasattr(route, 'methods'):
                    if 'admin-users' in route.path.lower():
                        print(f'FOUND ADMIN-USERS ROUTE: {route.path}, Methods: {route.methods}')
                        user_routes_found = True
                    elif '/login' in route.path.lower() and 'admin' in route.path:
                        print(f'FOUND ADMIN LOGIN ROUTE: {route.path}, Methods: {route.methods}')
                        login_routes_found = True

        if not user_routes_found:
            print('No admin-users routes found in main app')
        if not login_routes_found:
            print('No admin login routes found in main app')

        print('\n=== 搜索所有包含user的路由 ===')
        for route in app.routes:
            if hasattr(route, 'path') and 'user' in route.path.lower():
                methods = getattr(route, 'methods', 'N/A')
                print(f'USER ROUTE: {route.path}, Methods: {methods}')

        print('\n=== 搜索所有包含login的路由 ===')
        for route in app.routes:
            if hasattr(route, 'path') and 'login' in route.path.lower():
                methods = getattr(route, 'methods', 'N/A')
                print(f'LOGIN ROUTE: {route.path}, Methods: {methods}')
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()