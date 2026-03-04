"""
测试路由注册过程
"""
from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

def safe_import(module_path, router_name="router"):
    try:
        module = __import__(module_path, fromlist=[router_name])
        return getattr(module, router_name)
    except ImportError as e:
        logger.warning(f"Failed to import {module_path}.{router_name}: {e}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error importing {module_path}.{router_name}: {e}")
        return None

def main():
    print("开始测试路由注册过程...")
    
    # 模拟admin.py中的导入
    try:
        from backend.api.v1.users import router as users_router
        print("✓ users_router imported")
    except Exception as e:
        print(f"✗ users_router import failed: {e}")
        return

    try:
        from backend.api.v1.admin_user_management import router as admin_user_management_router
        print("✓ admin_user_management_router imported")
    except Exception as e:
        print(f"✗ admin_user_management_router import failed: {e}")
        return

    try:
        from backend.api.v1.frontend_user_management import router as frontend_user_management_router
        print("✓ frontend_user_management_router imported")
    except Exception as e:
        print(f"✗ frontend_user_management_router import failed: {e}")
        return

    try:
        from backend.api.v1.simple_user_api import router as simple_user_api_router
        print("✓ simple_user_api_router imported")
    except Exception as e:
        print(f"✗ simple_user_api_router import failed: {e}")
        return

    # 创建路由器
    router = APIRouter()
    print(f"初始路由数量: {len(router.routes)}")
    
    # 尝试注册路由 - 这是关键部分
    try:
        router.include_router(users_router, prefix="/users", tags=["users"])
        print(f"✓ users_router included, current count: {len(router.routes)}")
    except Exception as e:
        print(f"✗ users_router include failed: {e}")
    
    try:
        router.include_router(admin_user_management_router, prefix="/admin-users", tags=["admin-users"])
        print(f"✓ admin_user_management_router included, current count: {len(router.routes)}")
    except Exception as e:
        print(f"✗ admin_user_management_router include failed: {e}")
        
    try:
        router.include_router(frontend_user_management_router, prefix="/frontend-users", tags=["frontend-users"])
        print(f"✓ frontend_user_management_router included, current count: {len(router.routes)}")
    except Exception as e:
        print(f"✗ frontend_user_management_router include failed: {e}")
        
    try:
        router.include_router(simple_user_api_router, prefix="/simple-users", tags=["simple-users"])
        print(f"✓ simple_user_api_router included, current count: {len(router.routes)}")
    except Exception as e:
        print(f"✗ simple_user_api_router include failed: {e}")

    print(f"最终路由数量: {len(router.routes)}")
    
    # 检查是否包含预期的路由
    admin_users_found = False
    for route in router.routes:
        if hasattr(route, 'path') and 'admin-users' in route.path:
            print(f"Found route with admin-users: {route.path}")
            admin_users_found = True
    
    if admin_users_found:
        print("✓ admin-users routes are present")
    else:
        print("✗ admin-users routes are missing")
        
    # 检查所有路由
    print("\n所有注册的路由:")
    for i, route in enumerate(router.routes):
        if hasattr(route, 'path'):
            print(f"  {i+1:2d}. {route.path}")

if __name__ == "__main__":
    main()