#!/usr/bin/env python3
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from backend.database import engine
    from sqlalchemy import text
    
    with engine.connect() as conn:
        result = conn.execute(text('SELECT username, status FROM admin_users LIMIT 5'))
        users = result.fetchall()
        print(f"Found {len(users)} admin users:")
        for user in users:
            print(f"  - Username: {user[0]}, Status: {user[1]}")
            
except Exception as e:
    print(f"Error checking admin users: {e}")
    import traceback
    traceback.print_exc()