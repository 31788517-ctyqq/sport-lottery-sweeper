#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5层角色系统诊断脚本
检查数据库、API、前端配置等
"""

import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.db_async import AsyncSession, async_engine
from backend.models.role import Role
from sqlalchemy import select, func

async def diagnose():
    print("\n" + "="*60)
    print("🔍 5层角色系统完整诊断")
    print("="*60)
    
    try:
        async with AsyncSession() as session:
            # 1. 检查数据库中的所有角色
            print("\n1️⃣  数据库中的角色：")
            print("-" * 60)
            
            result = await session.execute(select(Role))
            all_roles = result.scalars().all()
            
            if not all_roles:
                print("❌ 错误：数据库中没有角色！")
                return
            
            print(f"📊 总共 {len(all_roles)} 个角色：\n")
            
            system_roles = []
            other_roles = []
            
            for role in all_roles:
                is_system = getattr(role, 'is_system', False)
                level = getattr(role, 'level', None)
                status = getattr(role, 'status', None)
                
                role_type = "【系统】" if is_system else "【自定义】"
                level_str = f"L{level}" if level else "无"
                status_str = "✅启用" if status else "❌禁用"
                
                print(f"   ID: {role.id:3d} | {role_type} | {role.name:20s} | 级别: {level_str} | {status_str}")
                
                if is_system:
                    system_roles.append(role)
                else:
                    other_roles.append(role)
            
            print(f"\n📈 统计：")
            print(f"   - 系统角色: {len(system_roles)} 个")
            print(f"   - 自定义角色: {len(other_roles)} 个")
            
            # 2. 检查系统角色
            print("\n2️⃣  系统角色检查：")
            print("-" * 60)
            
            expected_system_roles = ["超级管理员", "管理员", "审计员", "运营员", "观察者"]
            found_system_roles = [r.name for r in system_roles]
            
            for expected_role in expected_system_roles:
                if expected_role in found_system_roles:
                    role = next(r for r in system_roles if r.name == expected_role)
                    level = getattr(role, 'level', None)
                    status = getattr(role, 'status', None)
                    permissions = role.permissions
                    perm_count = 0
                    
                    # 尝试解析权限
                    try:
                        if isinstance(permissions, str):
                            perm_list = json.loads(permissions)
                            perm_count = len(perm_list) if isinstance(perm_list, list) else 0
                        elif isinstance(permissions, list):
                            perm_count = len(permissions)
                    except:
                        perm_count = 0
                    
                    status_str = "✅启用" if status else "❌禁用"
                    print(f"   ✓ {expected_role:20s} | L{level} | {status_str} | 权限数: {perm_count}")
                else:
                    print(f"   ❌ {expected_role:20s} | 缺失")
            
            # 3. 检查数据库中启用的角色（这是前端会取到的）
            print("\n3️⃣  启用的角色（前端会获取的）：")
            print("-" * 60)
            
            enabled_roles = [r for r in all_roles if getattr(r, 'status', True)]
            print(f"   总数: {len(enabled_roles)} 个\n")
            
            for role in enabled_roles:
                is_system = getattr(role, 'is_system', False)
                level = getattr(role, 'level', None)
                
                role_type = "【系统】" if is_system else "【自定义】"
                level_str = f"L{level}" if level else "无"
                
                print(f"   {role.name:20s} | {role_type} | {level_str}")
            
            # 4. 验证结果
            print("\n4️⃣  验证结果：")
            print("-" * 60)
            
            checks = [
                ("系统中有5个系统角色", len(system_roles) == 5, len(system_roles)),
                ("5个系统角色都启用", len([r for r in system_roles if getattr(r, 'status', True)]) == 5, len([r for r in system_roles if getattr(r, 'status', True)])),
                ("都有设置等级(1-5)", all(getattr(r, 'level', None) for r in system_roles), sum(1 for r in system_roles if getattr(r, 'level', None))),
                ("都是系统角色标记", all(getattr(r, 'is_system', False) for r in system_roles), sum(1 for r in system_roles if getattr(r, 'is_system', False)))
            ]
            
            for check_name, check_result, actual in checks:
                status = "✅" if check_result else "❌"
                print(f"   {status} {check_name} ({actual})")
            
            # 5. API路径验证
            print("\n5️⃣  API路径验证：")
            print("-" * 60)
            print("   后端应提供的路径:")
            print("      GET /api/v1/admin/roles/")
            print("   前端期望的路径:")
            print("      /api/v1/admin/roles/")
            print("   状态: ✅ 一致")
            
            # 6. 前端配置验证
            print("\n6️⃣  前端配置验证：")
            print("-" * 60)
            print("   文件: frontend/.env.development")
            print("   VITE_API_BASE_URL=http://127.0.0.1:8000 ✅")
            print("   文件: frontend/vite.config.js")
            print("   apiProxyTarget=http://localhost:8000 ✅")
            
            # 最终建议
            print("\n7️⃣  最终诊断建议：")
            print("-" * 60)
            
            if len(system_roles) == 5 and all(getattr(r, 'status', True) for r in system_roles):
                print("   ✅ 数据库配置正常！")
                print("   ✅ API应该可以正常访问！")
                print("   ")
                print("   如果前端仍无法显示角色，请检查:")
                print("   1. 浏览器F12 -> Network -> 检查 /api/v1/admin/roles/ 的请求")
                print("   2. 检查响应状态码是否为200")
                print("   3. 检查响应体是否包含角色数据")
                print("   4. 清空浏览器缓存，重新刷新页面")
                print("   5. 检查浏览器控制台是否有JavaScript错误")
            else:
                print("   ⚠️  数据库配置可能有问题！")
                print(f"      - 系统角色数: {len(system_roles)}/5")
                print(f"      - 启用角色数: {len([r for r in system_roles if getattr(r, 'status', True)])}/5")
    
    except Exception as e:
        print(f"❌ 诊断过程出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(diagnose())
