#!/usr/bin/env python3
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_login_logic():
    from backend.database import engine
    from sqlalchemy.orm import sessionmaker
    from backend.models.admin_user import AdminUser, AdminStatusEnum
    from backend.core.security import verify_password
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 查询用户
        user = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not user:
            print("❌ 用户不存在")
            return
        
        print(f"用户存在: {user.username}")
        print(f"用户状态: {user.status}")
        print(f"用户状态类型: {type(user.status)}")
        print(f"AdminStatusEnum.ACTIVE: {AdminStatusEnum.ACTIVE}")
        print(f"AdminStatusEnum.ACTIVE 类型: {type(AdminStatusEnum.ACTIVE)}")
        
        # 检查状态
        status_check_1 = not user.status
        status_check_2 = user.status != AdminStatusEnum.ACTIVE
        status_check_final = status_check_1 or status_check_2
        
        print(f"not user.status: {status_check_1}")
        print(f"user.status != AdminStatusEnum.ACTIVE: {status_check_2}")
        print(f"最终状态检查结果: {status_check_final}")
        
        if status_check_final:
            print("❌ 用户状态检查失败")
            return
        
        # 验证密码
        password_valid = verify_password("admin123", user.password_hash)
        print(f"密码验证结果: {password_valid}")
        
        if password_valid:
            print("✅ 登录逻辑通过！")
        else:
            print("❌ 密码验证失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_login_logic()