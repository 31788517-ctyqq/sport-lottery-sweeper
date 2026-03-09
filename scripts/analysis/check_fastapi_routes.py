"""
检查FastAPI应用的实际路由
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def print_all_routes(app, prefix=""):
    """递归打印FastAPI应用的所有路由"""
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            # 这是一个APIRoute
            print(f"{prefix}PATH: {route.path}")
            print(f"{prefix}METHODS: {route.methods}")
            print(f"{prefix}NAME: {getattr(route, 'name', 'unknown')}")
            print(f"{prefix}---")
        elif hasattr(route, 'routes'):
            # 这是一个路由器，递归处理
            sub_prefix = prefix + f"[{getattr(route, 'path', 'NO_PATH')}] "
            print_all_routes(route, sub_prefix)

def main():
    try:
        # 尝试直接从main导入app
        from backend.main import app
        print("=== FastAPI应用路由结构 ===")
        print_all_routes(app)
        
        print("\n=== 搜索包含'user'的路由 ===")
        # 专门搜索用户相关路由
        for route in app.routes:
            if hasattr(route, 'path') and 'user' in route.path.lower():
                print(f"USER ROUTE: {route.path}, METHODS: {route.methods}")
                
        print("\n=== 搜索包含'admin'的路由 ===")
        # 专门搜索admin相关路由
        for route in app.routes:
            if hasattr(route, 'path') and 'admin' in route.path.lower():
                print(f"ADMIN ROUTE: {route.path}, METHODS: {route.methods}")
                
        print("\n=== 搜索登录相关路由 ===")
        # 专门搜索登录相关路由
        for route in app.routes:
            if hasattr(route, 'path') and 'login' in route.path.lower():
                print(f"LOGIN ROUTE: {route.path}, METHODS: {route.methods}")
        
    except ImportError as e:
        print(f"无法导入backend.main: {e}")
        print("尝试其他导入方式...")
        
        # 尝试手动构造应用
        try:
            from backend.api.v1.admin import router as admin_router
            print("\n=== Admin路由内容 ===")
            print_all_routes(admin_router, "ADMIN: ")
        except Exception as e:
            print(f"无法导入admin路由: {e}")

if __name__ == "__main__":
    main()