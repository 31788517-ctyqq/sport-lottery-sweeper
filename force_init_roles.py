#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强制重新初始化5层角色系统
这个脚本直接使用async_engine，不依赖于dependency injection
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from backend.models.role import Role
from backend.models.base import Base

# 5层角色配置
ROLES_CONFIG = [
    {
        "name": "超级管理员",
        "level": 5,
        "description": "系统所有者，拥有所有权限，负责系统安全和权限策略制定",
        "is_system": True,
        "permissions": list(range(101, 1010))
    },
    {
        "name": "管理员",
        "level": 4,
        "description": "部门主管，拥有除系统配置外的大部分管理权限",
        "is_system": True,
        "permissions": [102, 103, 104, 106, 107, 202, 302, 303, 304, 402, 403, 404, 502, 503, 504, 505, 602, 603, 702, 703, 704, 706, 707, 802, 803, 804, 805, 902, 903, 904, 1005, 1007]
    },
    {
        "name": "审计员",
        "level": 3,
        "description": "合规监督者，拥有查看日志和生成报表的权限",
        "is_system": True,
        "permissions": [102, 202, 302, 402, 502, 505, 602, 702, 703, 802, 804, 1005, 1006, 1007]
    },
    {
        "name": "运营员",
        "level": 2,
        "description": "日常执行者，拥有数据维护、任务执行和数据分析权限",
        "is_system": True,
        "permissions": [102, 202, 302, 403, 504, 505, 602, 603, 702, 703, 704, 706, 707, 802, 804, 805, 902, 903, 904, 1005]
    },
    {
        "name": "观察者",
        "level": 1,
        "description": "只读用户，仅拥有查看权限，无任何修改、执行、删除权限",
        "is_system": True,
        "permissions": [102, 202, 302, 402, 502, 602, 702, 706, 802, 804, 1005, 1007]
    }
]

async def init_roles_force():
    """强制重新初始化5层角色"""
    # 创建异步引擎 (使用应用默认配置)
    from backend.database_async import async_engine
    
    print("\n" + "="*80)
    print("  强制重新初始化5层角色系统")
    print("="*80)
    
    # 创建表
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ 数据库表已创建")
    
    # 创建Session类
    AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        print("\n========== 清空现有角色 ==========")
        # 删除所有现有角色
        await session.execute(select(Role))
        result = await session.execute(select(func.count(Role.id)))
        existing_count = result.scalar()
        print(f"数据库中现有角色数: {existing_count}")
        
        if existing_count > 0:
            print("删除现有角色...", end="")
            await session.execute(select(Role).delete())
            await session.commit()
            print(" ✓完成")
        
        print("\n========== 创建5层角色 ==========")
        for config in ROLES_CONFIG:
            role = Role(
                name=config["name"],
                level=config["level"],
                description=config["description"],
                is_system=config["is_system"],
                permissions=json.dumps(config["permissions"], ensure_ascii=False),
                status=True,  # 确保启用
                sort_order=6 - config["level"]
            )
            session.add(role)
            print(f"✓ 创建角色: {config['name']} (L{config['level']})")
        
        await session.commit()
        print("\n✅ 所有角色已提交到数据库")
        
        # 验证
        print("\n========== 验证角色 ==========")
        result = await session.execute(select(Role).order_by(Role.level.desc()))
        all_roles = result.scalars().all()
        
        print(f"\n📊 数据库中现有 {len(all_roles)} 个角色:\n")
        for role in all_roles:
            perms = json.loads(role.permissions or '[]') if isinstance(role.permissions, str) else role.permissions
            print(f"[{role.level}] {role.name}")
            print(f"    Level: {role.level} | System: {role.is_system} | Status: {role.status}")
            print(f"    Permissions: {len(perms) if isinstance(perms, (list, dict)) else 0}")
        
        print("\n" + "="*80)
        system_roles = [r for r in all_roles if r.is_system]
        print(f"✅ 系统角色总数: {len(system_roles)}")
        print("="*80)

if __name__ == "__main__":
    try:
        asyncio.run(init_roles_force())
        print("\n✨ 初始化完成！\n")
    except Exception as e:
        print(f"\n❌ 初始化失败:\n{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
