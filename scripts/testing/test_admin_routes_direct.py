"""
直接测试admin模块路由注册
"""
import sys
import os
sys.path.insert(0, os.getcwd())

def test_admin_routes():
    print("正在直接测试admin模块路由注册...")
    
    # 导入前清理模块缓存
    modules_to_clear = [k for k in sys.modules.keys() if k.startswith('backend')]
    for mod in modules_to_clear:
        del sys.modules[mod]
    
    try:
        # 导入admin模块
        from backend.api.v1 import admin
        
        print(f"Admin模块导入成功，当前路由数量: {len(admin.router.routes)}")
        
        # 检查是否包含预期的路由
        found_admin_users = False
        found_login = False
        
        for route in admin.router.routes:
            if hasattr(route, 'path'):
                if 'admin-users' in route.path:
                    print(f"✅ 找到admin-users路由: {route.path}")
                    found_admin_users = True
                elif 'login' in route.path and route.path.endswith('/login'):
                    print(f"✅ 找到login路由: {route.path}")
                    found_login = True
        
        if not found_admin_users:
            print("❌ 未找到admin-users路由")
        
        if not found_login:
            print("❌ 未找到login路由")
            
        # 输出前几个路由供参考
        print(f"\n前5个路由:")
        for i, route in enumerate(admin.router.routes[:5]):
            if hasattr(route, 'path'):
                print(f"  {i+1}. {route.path}")
        
        return found_admin_users, found_login
        
    except Exception as e:
        print(f"❌ 导入admin模块失败: {e}")
        import traceback
        traceback.print_exc()
        return False, False

if __name__ == "__main__":
    test_admin_routes()