import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text

# 使用测试数据库路径
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sport_lottery_test.db")
print(f"Checking database: {db_path}")

engine = create_engine(f"sqlite:///{db_path}")

with engine.connect() as conn:
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")).fetchall()
    tables = [r[0] for r in result]
    print('Tables in database:', tables)
    
    if 'users' in tables:
        print("✓ users table exists")
    else:
        print("✗ users table does NOT exist")