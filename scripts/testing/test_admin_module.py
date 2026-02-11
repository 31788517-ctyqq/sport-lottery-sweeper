"""
专门测试admin模块的脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def main():
    try:
        print("开始导入admin模块...")
        import backend.api.v1.admin
        print("admin模块导入成功")
        
        print(f"admin模块中的router有 {len(backend.api.v1.admin.router.routes)} 个路由")
        
        # 检查admin模块中是否包含admin-users路由
        admin_users_found = False
        login_found = False
        
        for route in backend.api.v1.admin.router.routes:
            if hasattr(route, 'path'):
                if 'admin-users' in route.path:
                    print(f"找到admin-users路由: {route.path}")
                    admin_users_found = True
                elif '/login' in route.path and hasattr(route, 'methods'):
                    print(f"找到登录路由: {route.path}, 方法: {route.methods}")
                    login_found = True
        
        if not admin_users_found:
            print("没有找到admin-users路由")
            
        if not login_found:
            print("没有找到登录路由")
            
        # 检查模块中导入的路由变量
        print("\n测试直接导入各个路由模块...")
        try:
            from backend.api.v1.admin_user_management import router as admin_user_management_router
            print(f"admin_user_management路由有 {len(admin_user_management_router.routes)} 个路由")
        except Exception as e:
            print(f"导入admin_user_management路由失败: {e}")
        
        # 检查admin模块中的所有属性
        print("\nadmin模块中的属性:")
        for attr in dir(backend.api.v1.admin):
            if not attr.startswith('__'):
                print(f"  - {attr}")
        
    except Exception as e:
        print(f"导入admin模块失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()