from backend.main import app

def find_user_routes(routes, prefix=''):
    for route in routes:
        if hasattr(route, 'path') and ('user' in route.path.lower() or 'admin' in route.path.lower()):
            if hasattr(route, 'methods'):
                print(f'路径: {prefix}{route.path}')
                print(f'方法: {getattr(route, "methods", "N/A")}')
                print(f'名称: {getattr(route, "name", "unknown")}')
                print('-' * 30)
            elif hasattr(route, 'routes'):
                # 这是一个子路由器
                sub_prefix = prefix + getattr(route, 'path', '')
                find_user_routes(route.routes, sub_prefix)

print('查找用户管理相关路由...')
find_user_routes(app.router.routes)