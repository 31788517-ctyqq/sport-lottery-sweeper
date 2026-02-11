#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from sqlalchemy import create_engine, text

def main():
    engine = create_engine('sqlite:///./data/sport_lottery.db')
    
    with engine.connect() as conn:
        # 检查roles表结构
        print("=== Roles table structure ===")
        result = conn.execute(text("PRAGMA table_info(roles)"))
        columns = result.fetchall()
        for col in columns:
            print(f"  {col[0]}: {col[1]} ({col[2]}) {'NOT NULL' if col[3] else ''} {'PRIMARY KEY' if col[5] else ''}")
        
        # 检查数据
        print("\n=== Roles table data ===")
        result = conn.execute(text("SELECT COUNT(*) FROM roles"))
        count = result.fetchone()[0]
        print(f"Total rows: {count}")
        
        if count > 0:
            result = conn.execute(text("SELECT * FROM roles LIMIT 10"))
            rows = result.fetchall()
            for i, row in enumerate(rows):
                print(f"  Row {i}: {row}")
        
        # 检查user_role_mappings表
        print("\n=== User_role_mappings table structure ===")
        result = conn.execute(text("PRAGMA table_info(user_role_mappings)"))
        columns = result.fetchall()
        for col in columns:
            print(f"  {col[0]}: {col[1]} ({col[2]})")
        
        # 检查数据
        result = conn.execute(text("SELECT COUNT(*) FROM user_role_mappings"))
        count = result.fetchone()[0]
        print(f"Total rows: {count}")

if __name__ == "__main__":
    main()