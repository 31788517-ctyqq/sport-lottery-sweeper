#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from sqlalchemy import create_engine
from backend.core.database import Base
from backend.models.role import Role
from backend.models.department import Department
import traceback

def main():
    db_url = "sqlite:///./sport_lottery.db"
    print(f"Connecting to {db_url}")
    engine = create_engine(db_url)
    
    # 检查roles表是否存在
    with engine.connect() as conn:
        result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='roles'")
        if result.fetchone():
            print("✓ 'roles' table already exists")
        else:
            print("✗ 'roles' table missing, creating...")
            try:
                # 创建roles表
                Role.__table__.create(bind=engine)
                print("  Created 'roles' table")
            except Exception as e:
                print(f"  Error creating roles table: {e}")
                traceback.print_exc()
        
        # 检查departments表是否存在
        result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='departments'")
        if result.fetchone():
            print("✓ 'departments' table already exists")
        else:
            print("✗ 'departments' table missing, creating...")
            try:
                Department.__table__.create(bind=engine)
                print("  Created 'departments' table")
            except Exception as e:
                print(f"  Error creating departments table: {e}")
                traceback.print_exc()
        
        # 列出所有表
        result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = result.fetchall()
        print(f"\nAll tables ({len(tables)}):")
        for t in tables:
            print(f"  - {t[0]}")

if __name__ == "__main__":
    main()