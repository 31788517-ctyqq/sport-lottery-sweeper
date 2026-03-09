"""
完整路由配置扫描脚本
"""
import sys
import os

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_routes(router, prefix="", indent=0):
    """递归打印路由信息"""
    if not hasattr(router, 'routes'):
        return
    
    for route in router.routes:
        route_prefix = "  " * indent
        
        if hasattr(route, 'path'):
            # APIRoute
            methods = getattr(route, 'methods', [])
            path = prefix + route.path
            name = getattr(route, 'name', 'N/A')
            print(f"{route_prefix}[APIRoute] {', '.join(methods):6s} {path:50s} ({name})")
        
        elif hasattr(route, 'routes'):
            # Nested Router (APIRouter mounted as a route)
            mount_path = getattr(route, 'path', '')
            full_prefix = prefix + mount_path
            print(f"{route_prefix}[Mount] {full_prefix}")
            print_routes(route, full_prefix, indent + 1)

def main():
    print_section("路由配置完整扫描")
    
    try:
        # 导入主应用
        print("\n🔍 导入主应用...")
        from backend.main import app
        print("✓ 主应用导入成功")
        
        # 获取所有路由
        print_section("主应用路由 (app)")
        print_routes(app)
        
        # 扫描API v1路由
        print_section("API v1 路由详情")
        from backend.api.v1 import router as v1_router
        print(f"📊 路由总数: {len(v1_router.routes)}")
        print_routes(v1_router, prefix="/api/v1")
        
        # 扫描Auth路由
        print_section("Auth 路由详情")
        from backend.api.v1 import auth
        print(f"📊 Auth 路由数: {len(auth.router.routes)}")
        print(f"📦 Auth router 对象: {auth.router}")
        print_routes(auth.router, prefix="/api/v1/auth")
        
        # 扫描Admin路由
        print_section("Admin 路由详情")
        from backend.api.v1 import admin
        print(f"📊 Admin 路由数: {len(admin.router.routes)}")
        print_routes(admin.router, prefix="/api/v1/admin")
        
        # 扫描管理后台路由
        print_section("管理后台路由详情 (/admin)")
        from backend.admin import admin_router
        print(f"📊 管理后台路由数: {len(admin_router.routes)}")
        print_routes(admin_router, prefix="/admin")
        
        # 检查路由注册情况
        print_section("路由注册检查")
        
        # 检查 /api/v1/auth/login 是否存在
        auth_login_found = False
        for route in app.routes:
            if hasattr(route, 'path'):
                if '/auth/login' in route.path:
                    auth_login_found = True
                    print(f"✓ 找到 auth/login 路由: {route.path}")
        
        if not auth_login_found:
            # 深度搜索
            print("\n⚠ 在主应用中未找到 /auth/login 路由，进行深度搜索...")
            
            def deep_search(router, prefix="", level=0):
                if level > 5:  # 防止无限递归
                    return
                for route in getattr(router, 'routes', []):
                    if hasattr(route, 'path'):
                        full_path = prefix + route.path
                        if 'login' in full_path.lower():
                            print(f"  {'  ' * level}找到: {full_path}")
                    if hasattr(route, 'routes'):
                        mount_path = getattr(route, 'path', '')
                        deep_search(route, prefix + mount_path, level + 1)
            
            deep_search(app)
        
        # 总结
        print_section("总结")
        print(f"✓ 主应用路由总数: {len(app.routes)}")
        print(f"✓ API v1 路由数: {len(v1_router.routes)}")
        print(f"✓ Auth 路由数: {len(auth.router.routes)}")
        print(f"✓ Admin 路由数: {len(admin.router.routes)}")
        print(f"✓ 管理后台路由数: {len(admin_router.routes)}")
        
        # 检查配置
        print_section("配置信息")
        from backend.config import settings
        print(f"API_V1_STR: {settings.API_V1_STR}")
        print(f"HOST: {settings.HOST}")
        print(f"PORT: {settings.PORT}")
        print(f"DEBUG: {settings.DEBUG}")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
