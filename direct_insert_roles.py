#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接向SQLite数据库插入5个系统角色
"""
import sqlite3
import json

db_path = "data/sport_lottery.db"

ROLES = [
    {
        "name": "超级管理员",
        "level": 5,
        "description": "系统所有者，拥有所有权限，负责系统安全和权限策略制定",
        "permissions": list(range(101, 1010))
    },
    {
        "name": "管理员",
        "level": 4,
        "description": "部门主管，拥有除系统配置外的大部分管理权限",
        "permissions": [102, 103, 104, 106, 107, 202, 302, 303, 304, 402, 403, 404, 502, 503, 504, 505, 602, 603, 702, 703, 704, 706, 707, 802, 803, 804, 805, 902, 903, 904, 1005, 1007]
    },
    {
        "name": "审计员",
        "level": 3,
        "description": "合规监督者，拥有查看日志和生成报表的权限",
        "permissions": [102, 202, 302, 402, 502, 505, 602, 702, 703, 802, 804, 1005, 1006, 1007]
    },
    {
        "name": "运营员",
        "level": 2,
        "description": "日常执行者，拥有数据维护、任务执行和数据分析权限",
        "permissions": [102, 202, 302, 403, 504, 505, 602, 603, 702, 703, 704, 706, 707, 802, 804, 805, 902, 903, 904, 1005]
    },
    {
        "name": "观察者",
        "level": 1,
        "description": "只读用户，仅拥有查看权限，无任何修改、执行、删除权限",
        "permissions": [102, 202, 302, 402, 502, 602, 702, 706, 802, 804, 1005, 1007]
    }
]

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("  直接插入5个系统角色到数据库")
    print("="*80)
    
    # 先删除所有系统角色
    cursor.execute("DELETE FROM roles WHERE is_system = 1")
    print("✓ 清除现有系统角色")
    
    # 插入新角色
    for idx, role in enumerate(ROLES, 1):
        permissions_json = json.dumps(role["permissions"], ensure_ascii=False)
        cursor.execute("""
            INSERT INTO roles (name, level, description, is_system, status, permissions, sort_order)
            VALUES (?, ?, ?, 1, 1, ?, ?)
        """, (role["name"], role["level"], role["description"], permissions_json, 6 - role["level"]))
        print(f"✓ 插入角色: {role['name']} (L{role['level']})")
    
    conn.commit()
    print("\n✅ 全部插入成功！\n")
    
    # 验证
    print("="*80)
    print("  验证结果")
    print("="*80)
    cursor.execute("SELECT id, name, level, is_system, status FROM roles WHERE is_system = 1 ORDER BY level DESC")
    rows = cursor.fetchall()
    
    for row in rows:
        role_id, name, level, is_system, status = row
        print(f"[{role_id}] {name:20} L{level} | System={is_system} | Status={status}")
    
    print(f"\n总计: {len(rows)} 个系统角色")
    
    conn.close()
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
