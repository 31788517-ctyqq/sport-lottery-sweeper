#!/usr/bin/env python3
import os
import sys

# 设置环境
os.environ['FULL_API_MODE'] = 'true'
sys.path.insert(0, '.')

print("="*70)
print("Testing lottery module import...")
print("="*70)

try:
    from backend.api.v1 import lottery
    print("\n✓ SUCCESS: lottery module imported")
    print(f"\nRouter object: {lottery.router}")
    print(f"Router prefix: {repr(lottery.router.prefix)}")
    print(f"\nRoutes count: {len(lottery.router.routes)}")
    
    print("\nRoutes:")
    for i, route in enumerate(lottery.router.routes):
        if hasattr(route, 'path'):
            print(f"  {i}: {route.path}")
        else:
            print(f"  {i}: {route} (no path)")
    
except Exception as e:
    print(f"\n✗ FAILED: {type(e).__name__}")
    print(f"Error: {str(e)}")
    import traceback
    print("\nTraceback:")
    traceback.print_exc()

print("\n" + "="*70)
print("Testing main app routes...")
print("="*70)

try:
    from backend.main import app
    print(f"\nTotal routes: {len(app.routes)}")
    
    lottery_routes = [r for r in app.routes if hasattr(r, 'path') and 'lottery' in r.path]
    print(f"Lottery routes found: {len(lottery_routes)}")
    
    if lottery_routes:
        print("\nLottery routes:")
        for route in lottery_routes:
            print(f"  {route.path}")
    else:
        print("\nNo lottery routes found in main app")
        
        # List all routes
        print("\nAll routes:")
        for route in app.routes[:20]:
            if hasattr(route, 'path'):
                print(f"  {route.path}")

except Exception as e:
    print(f"\n✗ Failed to load main app: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
