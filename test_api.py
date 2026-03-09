#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通过API查询角色列表
"""
import requests
import json

print("🔍 查询API: http://localhost:8000/api/v1/admin/roles/?status=active")
print("="*80)

try:
    response = requests.get("http://localhost:8000/api/v1/admin/roles/?status=active", timeout=5)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        roles = data.get('data', [])
        
        print(f"\n📊 API返回了 {len(roles)} 个角色:\n")
        
        for idx, role in enumerate(roles, 1):
            level = role.get('level', 'N/A')
            is_system = role.get('is_system', False)
            status = role.get('status', False)
            permissions = role.get('permissions', [])
            
            if isinstance(permissions, str):
                try:
                    permissions = json.loads(permissions)
                except:
                    permissions = []
            
            perm_count = len(permissions) if isinstance(permissions, (list, dict)) else 0
            
            print(f"[{idx}] {role.get('name', 'N/A')}")
            print(f"    Level: {level} | System: {is_system} | Status: {status} | Permissions: {perm_count}")
        
        # 统计
        print(f"\n{'='*80}")
        system_roles = [r for r in roles if r.get('is_system')]
        print(f"系统角色: {len(system_roles)}")
        for role in system_roles:
            print(f"  ✓ {role.get('name')} (L{role.get('level')})")
    else:
        print(f"错误: {response.text}")

except requests.exceptions.ConnectionError:
    print("❌ 无法连接到后端服务 (http://localhost:8000)")
    print("请确保后端服务在8000端口运行")
except Exception as e:
    print(f"❌ 错误: {e}")
