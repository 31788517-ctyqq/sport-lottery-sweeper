# 快速路由检查
import sys
sys.path.insert(0, '.')

from backend.api.v1.sp_data_source import router

print("SP数据源路由:")
for r in router.routes:
    if hasattr(r, 'path'):
        methods = getattr(r, 'methods', 'NO_METHOD')
        path = getattr(r, 'path', 'NO_PATH')
        print(f"  {methods} {path}")

print("\n完整API路径 (加上 /admin/sp 前缀):")
for r in router.routes:
    if hasattr(r, 'path'):
        methods = getattr(r, 'methods', 'NO_METHOD')
        path = getattr(r, 'path', 'NO_PATH')
        full_path = "/admin/sp" + path
        print(f"  {methods} {full_path}")