#!/usr/bin/env python3
"""
填充roles表数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from backend.models.role import Role
from backend.config import settings

def main():
    print("Populating roles table...")
    # 使用同步数据库连接
    engine = create_engine(settings.DATABASE_URL, echo=False)
    
    with Session(engine) as session:
        # 检查是否已有角色
        existing = session.query(Role).count()
        if existing > 0:
            print(f"Roles table already has {existing} records. Skipping.")
            return
        
        # 定义默认角色
        default_roles = [
            {
                "name": "超级管理员",
                "description": "系统最高权限管理员，拥有所有权限",
                "permissions": "[]",  # 空JSON数组，表示所有权限
                "status": True,
                "sort_order": 1
            },
            {
                "name": "管理员",
                "description": "系统管理员，拥有大部分管理权限",
                "permissions": "[]",
                "status": True,
                "sort_order": 2
            },
            {
                "name": "内容审核员",
                "description": "负责内容审核和用户管理",
                "permissions": "[]",
                "status": True,
                "sort_order": 3
            },
            {
                "name": "审计员",
                "description": "查看系统日志和审计报告",
                "permissions": "[]",
                "status": True,
                "sort_order": 4
            },
            {
                "name": "运营人员",
                "description": "数据录入和维护",
                "permissions": "[]",
                "status": True,
                "sort_order": 5
            }
        ]
        
        for role_data in default_roles:
            role = Role(**role_data)
            session.add(role)
        
        session.commit()
        print(f"Inserted {len(default_roles)} default roles.")
        
        # 验证插入
        roles = session.query(Role).all()
        for r in roles:
            print(f"  - {r.id}: {r.name} (status: {r.status})")

if __name__ == "__main__":
    main()