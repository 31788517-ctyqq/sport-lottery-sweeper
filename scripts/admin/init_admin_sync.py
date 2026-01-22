import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.core.database import SessionLocal
from backend.models.user import User, UserTypeEnum, UserStatusEnum
from backend.core.security import get_password_hash

def create_admin_user():
    """创建管理员用户"""
    db = SessionLocal()
    try:
        # 检查是否已存在admin用户
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("管理员用户已存在")
            return
        
        # 创建管理员用户
        admin_user = User(
            username="admin",
            email="admin@sports-lottery.local",
            password_hash=get_password_hash("Admin123!@#"),
            user_type=UserTypeEnum.ADMIN,
            status=UserStatusEnum.ACTIVE,
            is_verified=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print("管理员用户创建成功！")
        print(f"用户名: {admin_user.username}")
        print(f"邮箱: {admin_user.email}")
        print(f"用户类型: {admin_user.user_type}")
        print(f"状态: {admin_user.status}")
        
    except Exception as e:
        print(f"创建管理员用户时出错: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()