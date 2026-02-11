#!/usr/bin/env python3
"""
删除并重新创建roles表以匹配模型
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, MetaData, Table, text
from backend.config import settings

def main():
    print("Recreating roles table...")
    # 使用同步引擎
    engine = create_engine(settings.DATABASE_URL, echo=False)
    metadata = MetaData()
    
    # 反射现有表
    metadata.reflect(bind=engine)
    
    if 'roles' in metadata.tables:
        print("Dropping existing roles table...")
        roles_table = metadata.tables['roles']
        roles_table.drop(engine)
        print("Table dropped.")
    
    # 现在创建表（通过SQLAlchemy模型）
    from backend.models.role import Role
    from backend.models.base import Base
    
    Base.metadata.create_all(engine, tables=[Role.__table__])
    print("Roles table created with correct schema.")
    
    # 插入默认数据
    with engine.connect() as conn:
        # 检查是否为空
        result = conn.execute("SELECT COUNT(*) FROM roles").scalar()
        if result == 0:
            print("Inserting default roles...")
            default_roles = [
                ("超级管理员", "系统最高权限管理员，拥有所有权限", "[]", True, 1),
                ("管理员", "系统管理员，拥有大部分管理权限", "[]", True, 2),
                ("内容审核员", "负责内容审核和用户管理", "[]", True, 3),
                ("审计员", "查看系统日志和审计报告", "[]", True, 4),
                ("运营人员", "数据录入和维护", "[]", True, 5)
            ]
            for name, desc, perm, status, sort in default_roles:
                conn.execute(
                    "INSERT INTO roles (name, description, permissions, status, sort_order, created_at, updated_at) VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
                    (name, desc, perm, status, sort)
                )
            print("Default roles inserted.")
        
        # 验证
        rows = conn.execute("SELECT id, name, status FROM roles").fetchall()
        print("Roles in table:")
        for row in rows:
            print(f"  {row.id}: {row.name} (status: {row.status})")
    
    print("Done.")

if __name__ == "__main__":
    main()