#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试main.py的核心导入
"""
import sys
import os

# 添加backend目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_dir)
sys.path.insert(0, project_root)

print("=== 测试main.py导入 ===")
print(f"项目根目录: {project_root}")
print(f"Backend目录: {backend_dir}")
print(f"Python路径前3个: {sys.path[:3]}")

try:
    # 测试基础导入
    print("\n1. 测试基础模块导入...")
    import time
    import logging
    from datetime import datetime
    print("✓ 基础模块导入成功")
    
    # 测试FastAPI导入
    print("\n2. 测试FastAPI导入...")
    from fastapi import FastAPI
    print("✓ FastAPI导入成功")
    
    # 测试项目配置导入
    print("\n3. 测试项目配置导入...")
    from config import settings
    print(f"✓ 配置导入成功: {settings.APP_NAME}")
    
    # 测试核心模块导入
    print("\n4. 测试核心模块导入...")
    from core.middleware import RequestLoggingMiddleware
    print("✓ middleware导入成功")
    
    from core.async_initializer import get_async_initializer
    print("✓ async_initializer导入成功")
    
    # 测试utils模块导入
    print("\n5. 测试utils模块导入...")
    from utils.logging_config import setup_logging
    print("✓ logging_config导入成功")
    
    # 测试数据库导入
    print("\n6. 测试数据库导入...")
    from database import engine, Base, get_db
    print("✓ database导入成功")
    
    # 测试API路由导入
    print("\n7. 测试API路由导入...")
    from api.v1 import router as api_v1_router
    print("✓ api.v1导入成功")
    
    from admin.api.v1 import router as admin_v1_router
    print("✓ admin.api.v1导入成功")
    
    # 测试创建FastAPI应用
    print("\n8. 测试创建FastAPI应用...")
    app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)
    print("✓ FastAPI应用创建成功")
    
    # 配置中间件
    print("\n9. 测试配置中间件...")
    app.add_middleware(RequestLoggingMiddleware)
    print("✓ 中间件配置成功")
    
    # 配置路由
    print("\n10. 测试配置路由...")
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)
    app.include_router(admin_v1_router, prefix="/admin")
    print("✓ 路由配置成功")
    
    print("\n=== 所有测试通过! ===")
    print("✓ main.py的核心功能可以正常工作")
    print("✓ 可以启动后端服务")
    
except Exception as e:
    print(f"\n✗ 错误发生: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)