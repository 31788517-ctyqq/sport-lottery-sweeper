"""
简化路由扫描脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("开始扫描路由配置...")
print("=" * 80)

try:
    # 1. 检查 auth 模块
    print("\n[1] 检查 auth 模块...")
    from backend.api.v1 import auth
    print(f"  ✓ auth 模块导入成功")
    print(f"  ✓ auth.router: {auth.router}")
    print(f"  ✓ 路由数量: {len(auth.router.routes)}")
    
    for i, route in enumerate(auth.router.routes):
        if hasattr(route, 'path'):
            methods = ','.join(getattr(route, 'methods', []))
            print(f"    [{i+1}] {methods:6s} {route.path}")
    
    # 2. 检查 v1 路由器
    print("\n[2] 检查 v1 路由器...")
    from backend.api.v1 import router as v1_router
    print(f"  ✓ v1 router 导入成功")
    print(f"  ✓ 路由总数: {len(v1_router.routes)}")
    
    # 3. 检查 api 路由器
    print("\n[3] 检查 api 路由器...")
    from backend.api import router as api_router
    print(f"  ✓ api router 导入成功")
    print(f"  ✓ 路由总数: {len(api_router.routes)}")
    
    # 4. 检查主应用
    print("\n[4] 检查主应用...")
    from backend.main import app
    print(f"  ✓ 主应用导入成功")
    print(f"  ✓ 路由总数: {len(app.routes)}")
    
    # 5. 列出所有包含 'auth' 或 'login' 的路由
    print("\n[5] 搜索 auth/login 相关路由...")
    
    def search_routes(router, prefix="", depth=0):
        if depth > 10:
            return
        
        for route in getattr(router, 'routes', []):
            if hasattr(route, 'path'):
                full_path = prefix + route.path
                if 'auth' in full_path.lower() or 'login' in full_path.lower():
                    methods = ','.join(getattr(route, 'methods', []))
                    print(f"    {'  ' * depth}→ {methods:6s} {full_path}")
            
            # 递归搜索嵌套路由
            if hasattr(route, 'app') and hasattr(route.app, 'routes'):
                mount_path = getattr(route, 'path', '')
                search_routes(route.app, prefix + mount_path, depth + 1)
    
    search_routes(app)
    
    # 6. 检查配置
    print("\n[6] 检查配置...")
    from backend.config import settings
    print(f"  ✓ API_V1_STR: {settings.API_V1_STR}")
    print(f"  ✓ HOST: {settings.HOST}")
    print(f"  ✓ PORT: {settings.PORT}")
    
    print("\n" + "=" * 80)
    print("✓ 扫描完成!")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
