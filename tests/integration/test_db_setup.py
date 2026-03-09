#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库设置测试脚本
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("=== 数据库设置测试 ===")
print(f"项目根目录: {project_root}")
print(f"Python路径: {sys.path[:3]}")

try:
    # 测试导入
    print("\n1. 测试导入backend.models...")
    from backend.models import Base, AdminData, SystemConfig, CrawlerConfig, IntelligenceRecord
    print("✓ backend.models导入成功")
    print(f"  模型类: {[AdminData, SystemConfig, CrawlerConfig, IntelligenceRecord]}")
    
    print("\n2. 测试导入backend.config...")
    from backend.config import settings
    print("✓ backend.config导入成功")
    print(f"  数据库URL: {settings.DATABASE_URL}")
    
    print("\n3. 测试导入SQLAlchemy...")
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    print("✓ SQLAlchemy导入成功")
    
    print("\n4. 创建数据库引擎...")
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    print("✓ 数据库引擎创建成功")
    
    print("\n5. 创建所有表...")
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表创建成功")
    
    print("\n=== 测试完成 ===")
    print("所有数据库表已成功创建！")
    
except Exception as e:
    print(f"\n✗ 错误发生: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)