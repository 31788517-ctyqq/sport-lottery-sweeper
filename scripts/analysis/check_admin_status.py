import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import get_db
from backend.models.admin_user import AdminUser, AdminStatusEnum

def check_admin_status():
    """检查管理员用户状态"""
    from backend.database import engine
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 查找 admin 用户
        admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not admin:
            print("❌ 未找到 admin 用户")
            return
        
        print(f"管理员用户信息:")
        print(f"  ID: {admin.id}")
        print(f"  用户名: {admin.username}")
        print(f"  邮箱: {admin.email}")
        print(f"  角色: {admin.role}")
        print(f"  状态: {admin.status}")
        print(f"  是否启用双因素认证: {admin.two_factor_enabled}")
        print(f"  是否必须修改密码: {admin.must_change_password}")
        print(f"  密码过期时间: {admin.password_expires_at}")
        print(f"  最后登录时间: {admin.last_login_at}")
        
        # 检查状态
        if admin.status == AdminStatusEnum.ACTIVE:
            print("✅ 用户状态为 ACTIVE")
        else:
            print(f"⚠️  用户状态为 {admin.status.value}，需要修改为 ACTIVE")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_admin_status()