import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from backend.core.database import SessionLocal
    from backend.models.admin_user import AdminUser
    
    print("Testing database query...")
    
    db = SessionLocal()
    try:
        # 测试查询
        user = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if user:
            print(f"Found user: {user.username}")
            print(f"Email: {user.email}")
            print(f"Password hash: {user.password_hash[:30]}...")
            print(f"Role: {user.role}")
            print(f"Status: {user.status}")
        else:
            print("No user found")
    except Exception as e:
        print(f"Error querying: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        
except Exception as e:
    print(f"Error importing: {e}")
    import traceback
    traceback.print_exc()