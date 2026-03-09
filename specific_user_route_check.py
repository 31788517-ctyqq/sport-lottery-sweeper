from backend.api.v1.admin import router as admin_router

print("Admin路由中包含的子路由:")
for route in admin_router.routes:
    if hasattr(route, 'path') and hasattr(route, 'routes'):
        print(f"\n路由组: {getattr(route, 'name', 'unnamed')}")
        print(f"路径前缀: {route.path}")
        # 输出子路由
        for sub_route in route.routes:
            if hasattr(sub_route, 'path'):
                full_path = route.path + sub_route.path
                methods = getattr(sub_route, 'methods', 'N/A')
                name = getattr(sub_route, 'name', 'unknown')
                print(f"  路径: {full_path}")
                print(f"  方法: {methods}")
                print(f"  名称: {name}")
                print("  ---")
    elif hasattr(route, 'path'):
        path = route.path
        methods = getattr(route, 'methods', 'N/A')
        name = getattr(route, 'name', 'unknown')
        print(f"路径: {path}")
        print(f"方法: {methods}")
        print(f"名称: {name}")
        print("---")

# 特别检查用户管理路由
print("\n特别检查用户管理相关路由:")
for route in admin_router.routes:
    route_path = getattr(route, 'path', '')
    if 'user' in route_path.lower():
        print(f"找到用户相关路由: {route_path}")
        if hasattr(route, 'routes'):
            for sub_route in route.routes:
                if hasattr(sub_route, 'path'):
                    print(f"  子路由: {sub_route.path}")
                    print(f"  方法: {getattr(sub_route, 'methods', 'N/A')}")