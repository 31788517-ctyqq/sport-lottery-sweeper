#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接检查数据库中的角色数据
"""
import asyncio
from backend.database_async import AsyncSession, async_engine
from backend.models.role import Role
from sqlalchemy import select, func

async def check_roles():
    async with AsyncSession() as session:
        # 查询所有角色
        result = await session.execute(select(Role))
        all_roles = result.scalars().all()
        
        print(f"\n{'='*80}")
        print(f"📊 数据库中共有 {len(all_roles)} 个角色")
        print(f"{'='*80}\n")
        
        for idx, role in enumerate(all_roles, 1):
            print(f"[{idx}] ID: {role.id}")
            print(f"    名称: {role.name}")
            print(f"    描述: {role.description}")
            print(f"    级别: {getattr(role, 'level', 'N/A')}")
            print(f"    系统角色: {getattr(role, 'is_system', False)}")
            print(f"    状态: {getattr(role, 'status', False)}")
            permissions = getattr(role, 'permissions', None)
            if permissions:
                # 尝试解析权限
                import json
                try:
                    if isinstance(permissions, str):
                        perms = json.loads(permissions)
                        print(f"    权限数: {len(perms)}")
                    else:
                        print(f"    权限: {type(permissions)} - {len(permissions) if hasattr(permissions, '__len__') else 'N/A'}")
                except:
                    print(f"    权限: {permissions[:100] if isinstance(permissions, str) else type(permissions)}")
            print()
        
        # 统计系统角色
        system_roles = [r for r in all_roles if getattr(r, 'is_system', False)]
        print(f"{'='*80}")
        print(f"🔍 系统角色 (is_system=True): {len(system_roles)}")
        print(f"{'='*80}")
        for role in system_roles:
            print(f"  ✓ {role.name} (Level {getattr(role, 'level', 'N/A')})")
        
        # 统计启用状态的角色
        active_roles = [r for r in all_roles if getattr(r, 'status', False)]
        print(f"\n{'='*80}")
        print(f"✅ 启用状态 (status=True): {len(active_roles)}")
        print(f"{'='*80}")
        for role in active_roles:
            print(f"  ✓ {role.name}")
        
        # 统计启用的系统角色
        active_system_roles = [r for r in all_roles if getattr(r, 'status', False) and getattr(r, 'is_system', False)]
        print(f"\n{'='*80}")
        print(f"⭐ 启用的系统角色: {len(active_system_roles)}")
        print(f"{'='*80}")
        for role in active_system_roles:
            print(f"  ✓ {role.name} (L{getattr(role, 'level', '?')})")

if __name__ == '__main__':
    asyncio.run(check_roles())
