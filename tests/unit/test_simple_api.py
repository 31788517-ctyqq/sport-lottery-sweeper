#!/usr/bin/env python3
"""
简单的API路由测试
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.api.v1 import router
    print("[OK] API v1 router 导入成功")
    
    # 检查路由中是否包含auth路由
    auth_routes = [route for route in router.routes if '/auth' in str(route.path)]
    if auth_routes:
        print(f"[OK] 找到 {len(auth_routes)} 个 auth 路由")
    else:
        print("[ERROR] 未找到 auth 路由")
        
    # 检查路由中是否包含crawler路由
    crawler_routes = [route for route in router.routes if '/crawler' in str(route.path)]
    if crawler_routes:
        print(f"[OK] 找到 {len(crawler_routes)} 个 crawler 路由")
    else:
        print("[ERROR] 未找到 crawler 路由")
        
except Exception as e:
    print(f"[ERROR] API v1 router 导入失败: {e}")
    import traceback
    traceback.print_exc()