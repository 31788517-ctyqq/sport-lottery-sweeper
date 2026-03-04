#!/usr/bin/env python3
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_full_login():
    from backend.database import get_db
    from backend.models.admin_user import AdminUser
    from backend.core.security import verify_password
    
    # 获取数据库会话
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # 模拟登录数据
        username = "admin"
        password = "admin123"
        
        # 查询用户
        user = db.query(AdminUser).filter(AdminUser.username == username).first()
        if not user:
            print("❌ 用户不存在")
            return
        
        print(f"✅ 找到用户: {user.username}")
        print(f"   密码哈希: {user.password_hash}")
        
        # 验证密码
        password_valid = verify_password(password, user.password_hash)
        print(f"   密码验证结果: {password_valid}")
        
        if not password_valid:
            print("❌ 密码验证失败")
            return
        
        # 检查用户状态
        from backend.models.admin_user import AdminStatusEnum
        if not user.status or user.status != AdminStatusEnum.ACTIVE:
            print(f"❌ 用户状态无效: {user.status}")
            return
        
        print("✅ 登录成功！")
        
    except Exception as e:
        print(f"❌ 登录过程出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_full_login()