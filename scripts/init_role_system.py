#!/usr/bin/env python3
"""
初始化脚本：创建5层角色体系和完整权限结构
运行方式: python scripts/init_role_system.py
"""
import asyncio
import json
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database_async import get_async_db, async_engine
from backend.models.role import Role, RoleLevelEnum
from backend.models.base import Base


# 定义5层角色
ROLES_CONFIG = [
    {
        "name": "超级管理员",
        "level": 5,
        "description": "系统所有者，拥有所有权限，负责系统安全和权限策略制定",
        "is_system": True,
        "permissions": list(range(101, 1010))  # 所有权限
    },
    {
        "name": "管理员",
        "level": 4,
        "description": "部门主管，拥有除系统配置外的大部分管理权限",
        "is_system": True,
        "permissions": [
            # 用户系统管理（除删除用户）
            102, 103, 104, 106, 107,
            # 角色权限（仅查看）
            202,
            # 部门管理
            302, 303, 304,
            # 数据源管理
            402, 403, 404,
            # 爬虫任务
            502, 503, 504, 505,
            # 爬虫监控
            602, 603,
            # 数据中心
            702, 703, 704, 706, 707,
            # IP池和请求头
            802, 803, 804, 805,
            # 分析工具
            902, 903, 904,
            # 日志和审计（仅查看）
            1005, 1007
        ]
    },
    {
        "name": "审计员",
        "level": 3,
        "description": "合规监督者，拥有查看日志和生成报表的权限",
        "is_system": True,
        "permissions": [
            # 查看用户和角色
            102, 202,
            # 查看部门
            302,
            # 查看数据源和任务
            402, 502, 505,
            # 查看爬虫监控
            602,
            # 查看数据
            702, 703,
            # 查看IP池和请求头
            802, 804,
            # 日志审计（重点权限）
            1005, 1006, 1007
        ]
    },
    {
        "name": "运营员",
        "level": 2,
        "description": "日常执行者，拥有数据维护、任务执行和数据分析权限",
        "is_system": True,
        "permissions": [
            # 查看部门
            302,
            # 数据源管理
            402, 403, 404,
            # 爬虫任务
            502, 503, 504, 505,
            # 爬虫监控
            602,
            # 数据中心
            702, 703, 704, 706,
            # IP池和请求头
            802, 803, 804, 805,
            # 分析工具
            902, 903, 904
        ]
    },
    {
        "name": "观察者",
        "level": 1,
        "description": "只读用户，仅拥有查看权限，无任何修改、执行、删除权限",
        "is_system": True,
        "permissions": [
            # 仅查看权限
            102,  # 查看用户列表
            202,  # 查看角色列表
            302,  # 查看部门结构
            402,  # 查看数据源列表
            502,  # 查看爬虫任务
            602,  # 查看爬虫监控
            702,  # 数据查询权限
            706,  # 查看比赛数据
            802,  # 查看IP池
            804,  # 查看请求头模板
            1005,  # 查看系统日志
            1007  # 查看审计报表
        ]
    }
]


async def init_roles(db: AsyncSession):
    """初始化5层角色"""
    print("\n========== 初始化5层角色体系 ==========")
    
    for role_config in ROLES_CONFIG:
        # 检查角色是否已存在
        stmt = select(Role).where(Role.name == role_config["name"])
        existing = await db.scalar(stmt)
        
        if existing:
            print(f"✓ 角色 '{role_config['name']}' 已存在，更新权限...")
            existing.description = role_config["description"]
            existing.level = role_config["level"]
            existing.is_system = role_config["is_system"]
            existing.permissions = json.dumps(role_config["permissions"])
            existing.status = True  # 确保系统角色启用
            await db.merge(existing)
        else:
            print(f"✓ 创建角色 '{role_config['name']}' (L{role_config['level']})")
            role = Role(
                name=role_config["name"],
                description=role_config["description"],
                level=role_config["level"],
                is_system=role_config["is_system"],
                permissions=json.dumps(role_config["permissions"]),
                status=True,
                sort_order=6 - role_config["level"]  # 等级越高，排序越靠前
            )
            db.add(role)
    
    await db.commit()
    print(f"\n✅ 成功初始化 {len(ROLES_CONFIG)} 个角色")


async def main():
    """主函数"""
    try:
        print("\n" + "="*50)
        print("  角色系统初始化脚本")
        print("="*50)
        
        # 创建表结构（如果不存在）
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # 初始化数据
        async for db in get_async_db():
            await init_roles(db)
            break
        
        print("\n✅ 初始化完成！")
        print("\n" + "="*50)
        print("  角色体系信息")
        print("="*50)
        
        async for db in get_async_db():
            stmt = select(Role).order_by(Role.level.desc())
            roles = (await db.execute(stmt)).scalars().all()
            
            for role in roles:
                permissions_count = len(json.loads(role.permissions or '[]'))
                level_name = ["观察者", "运营员", "审计员", "管理员", "超级管理员"][role.level - 1]
                print(f"\n  [{role.level}] {role.name} | {level_name} (L{role.level})")
                print(f"      描述: {role.description}")
                print(f"      权限数: {permissions_count}")
                print(f"      系统角色: {'是' if role.is_system else '否'}")
                print(f"      状态: {'启用' if role.status else '禁用'}")
            break
        
    except Exception as e:
        print(f"\n❌ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # 关闭连接
        await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
