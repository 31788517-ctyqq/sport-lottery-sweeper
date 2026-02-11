import sys
sys.path.insert(0, '.')

try:
    from backend.api.v1.admin import router as admin_router
    print("Successfully imported admin router")
    # 打印路由
    for route in admin_router.routes:
        print(f"  {route.path} -> {route.name}")
except Exception as e:
    print(f"Failed to import admin router: {e}")
    import traceback
    traceback.print_exc()

print("\n--- Trying to import logs router directly ---")
try:
    from backend.api.v1.admin.logs import router as logs_router
    print("Successfully imported logs router")
    for route in logs_router.routes:
        print(f"  {route.path} -> {route.name}")
except Exception as e:
    print(f"Failed to import logs router: {e}")
    import traceback
    traceback.print_exc()

print("\n--- Checking if logs module has errors ---")
try:
    import backend.api.v1.admin.logs
    print("logs module imported")
except Exception as e:
    print(f"logs module import error: {e}")
    import traceback
    traceback.print_exc()