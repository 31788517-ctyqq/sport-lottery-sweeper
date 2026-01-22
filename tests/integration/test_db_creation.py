#!/usr/bin/env python3
"""
测试数据库表创建
"""
import sys
import os

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 导入数据库模块以触发表创建
from backend.database import engine
from backend.models import Base

# 检查表是否存在
def check_tables():
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Existing tables: {tables}")
    return 'users' in tables

if __name__ == "__main__":
    print("Checking if tables exist...")
    if check_tables():
        print("✅ Users table exists!")
    else:
        print("❌ Users table does not exist!")
        # 尝试手动创建表
        print("Creating tables manually...")
        Base.metadata.create_all(bind=engine)
        if check_tables():
            print("✅ Tables created successfully!")
        else:
            print("❌ Failed to create tables!")