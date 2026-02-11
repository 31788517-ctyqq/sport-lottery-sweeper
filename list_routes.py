#!/usr/bin/env python3
"""
列出FastAPI应用的所有路由
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from backend.main import app

print("已注册的路由:")
print("=" * 80)

for route in app.routes:
    if hasattr(route, "path"):
        path = route.path
        methods = route.methods if hasattr(route, "methods") else []
        name = route.name if hasattr(route, "name") else ""
        print(f"{path} [{', '.join(methods)}] - {name}")

print(f"\n总路由数: {len(app.routes)}")

# 特别检查llm-providers路由
print("\n检查包含'llm-providers'的路由:")
for route in app.routes:
    if hasattr(route, "path") and "llm-providers" in route.path:
        print(f"找到: {route.path}")