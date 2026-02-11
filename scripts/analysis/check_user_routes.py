from backend.main import app
from starlette.routing import Router

def print_routes(router, prefix=''):
    for route in router.routes:
        if hasattr(route, 'methods'):
            print(f'路径: {prefix}{route.path}')
            print(f'方法: {route.methods}')
            print(f'名称: {getattr(route, "name", "unknown")}')
            print('-' * 30)
        elif hasattr(route, 'routes'):  # 如果是子路由器
            # 获取子路由器的前缀
            sub_prefix = prefix
            # 尝试获取子路由器的路径前缀
            if hasattr(route, 'path'):
                sub_prefix += route.path
            print_routes(route, sub_prefix)

print('后端路由注册情况:')
print_routes(app.router)
print('\n用户管理相关路由:')