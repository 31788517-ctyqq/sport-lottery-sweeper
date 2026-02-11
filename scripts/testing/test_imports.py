"""
测试各个路由模块的导入
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def test_imports():
    print("测试各个路由模块的导入...")
    
    modules_to_test = [
        ("backend.api.v1.admin.users", "router"),
        ("backend.api.v1.admin.admin_user_management", "router"), 
        ("backend.api.v1.admin.frontend_user_management", "router"),
        ("backend.api.v1.admin.simple_user_api", "router")
    ]
    
    for module_path, attr_name in modules_to_test:
        try:
            module = __import__(module_path, fromlist=[attr_name])
            router = getattr(module, attr_name)
            print(f"✓ {module_path} imported successfully, routes: {len(router.routes)}")
        except Exception as e:
            print(f"✗ {module_path} import failed: {e}")

if __name__ == "__main__":
    test_imports()