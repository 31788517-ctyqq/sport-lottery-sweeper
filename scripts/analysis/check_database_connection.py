import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 检查环境变量
print("Environment variables:")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"SECRET_KEY present: {'SECRET_KEY' in os.environ}")

try:
    from backend.database import engine, DATABASE_URL
    print(f"\nDatabase URL from backend.database: {DATABASE_URL}")
    
    # 执行查询测试
    from sqlalchemy import text
    with engine.connect() as conn:
        # 检查admin_users表
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM admin_users"))
            count = result.fetchone()[0]
            print(f"admin_users table count: {count}")
            
            # 检查是否有password_hash列
            result = conn.execute(text("PRAGMA table_info(admin_users)"))
            columns = result.fetchall()
            print("\nColumns in admin_users:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
                
            # 尝试查询password_hash
            result = conn.execute(text("SELECT username, password_hash FROM admin_users WHERE username = 'admin' LIMIT 1"))
            user = result.fetchone()
            if user:
                print(f"\nFound admin user: {user[0]}")
                print(f"password_hash: {user[1][:20]}...")
            else:
                print("\nNo admin user found")
                
        except Exception as e:
            print(f"Error querying database: {e}")
            import traceback
            traceback.print_exc()
            
except Exception as e:
    print(f"Error importing modules: {e}")
    import traceback
    traceback.print_exc()