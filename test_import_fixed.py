import sys
sys.path.insert(0, '.')

print("Testing import of admin router...")
try:
    from backend.api.v1.admin import router as admin_router
    print("SUCCESS: admin router imported")
    # 列出路由
    print(f"Number of routes: {len(admin_router.routes)}")
    for route in admin_router.routes:
        print(f"  {route.path} -> {route.name}")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting import of logs router...")
try:
    from backend.api.v1.admin.logs import router as logs_router
    print("SUCCESS: logs router imported")
    for route in logs_router.routes:
        print(f"  {route.path} -> {route.name}")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()