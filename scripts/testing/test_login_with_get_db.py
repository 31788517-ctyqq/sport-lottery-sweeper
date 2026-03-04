#!/usr/bin/env python3
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_login_with_get_db():
    from backend.database import get_db
    from backend.models.admin_user import AdminUser
    
    # 获取数据库会话
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # 查询用户
        user = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if user:
            print(f"✅ 通过get_db找到用户: {user.username}")
            print(f"   密码哈希: {user.password_hash}")
        else:
            print("❌ 通过get_db未找到用户")
            
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_login_with_get_db()