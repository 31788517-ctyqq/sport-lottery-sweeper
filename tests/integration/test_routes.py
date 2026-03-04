#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试SP数据源路由是否正确注册
"""
import sys
sys.path.insert(0, '.')

from backend.api.v1 import router
from fastapi.routing import APIRoute

print("=== SP相关路由列表 ===")
# 打印所有注册的路由
for route in router.routes:
    if hasattr(route, 'path') and ('/sp' in route.path or '/admin/sp' in route.path):
        methods = getattr(route, 'methods', set())
        path = getattr(route, 'path', '')
        print(f'{methods} {path}')

print("\n=== 检查特定路径 ===")
# 检查我们想要的路径是否存在
target_paths = [
    '/admin/sp/data-sources',
    '/admin/sp/data-source/{source_id}',
    '/admin/sp/data-source'
]

for target_path in target_paths:
    found = False
    for route in router.routes:
        if hasattr(route, 'path') and route.path == target_path:
            print(f'✓ 找到路由: {target_path}')
            found = True
            break
    if not found:
        print(f'✗ 未找到路由: {target_path}')