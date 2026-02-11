#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from sqlalchemy import create_engine, text
from backend.models.role import Role
from backend.core.database import Base

def main():
    # 创建数据库引擎
    engine = create_engine('sqlite:///./data/sport_lottery.db')
    
    # 检查当前有哪些表
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        print("Existing tables before create_all:")
        for t in tables:
            print(f"  - {t}")
    
    # 创建所有表（如果不存在）
    print("\nCreating missing tables from Base.metadata...")
    Base.metadata.create_all(bind=engine)
    print("Done.")
    
    # 验证roles表是否存在
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='roles'"))
        if result.fetchone():
            print("✓ 'roles' table now exists")
            # 检查表结构
            result = conn.execute(text("PRAGMA table_info(roles)"))
            columns = result.fetchall()
            print("  Columns:")
            for col in columns:
                print(f"    {col[1]} ({col[2]})")
        else:
            print("✗ 'roles' table still missing")
            
        # 列出所有表看看
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        print("\nAll tables after create_all:")
        for t in tables:
            print(f"  - {t}")

if __name__ == "__main__":
    main()