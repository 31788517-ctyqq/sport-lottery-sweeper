#!/usr/bin/env python3
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_login_with_backend_db():
    # 使用后端服务中的get_db函数
    from backend.database import get_db
    from backend.models.admin_user import AdminUser
    
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        username = "admin"
        user = db.query(AdminUser).filter(AdminUser.username == username).first()
        
        if user:
            print(f"✅ 通过后端get_db找到用户: {user.username}")
            print(f"   用户ID: {user.id}")
            print(f"   邮箱: {user.email}")
            print(f"   真实姓名: {user.real_name}")
            print(f"   角色: {user.role}")
            print(f"   状态: {user.status}")
            print(f"   密码哈希: {user.password_hash}")
        else:
            print("❌ 通过后端get_db未找到用户")
            
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_login_with_backend_db()