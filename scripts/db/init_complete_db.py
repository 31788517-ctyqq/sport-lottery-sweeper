"""
完整的数据库初始化脚本
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.security import get_password_hash
from backend.models.user import User, UserStatusEnum, UserRoleEnum
from backend.models.base import Base
from backend.config import settings

def init_database():
    """初始化数据库"""
    # 创建数据库引擎
    engine = create_engine(settings.DATABASE_URL, echo=False)
    
    # 删除所有现有表
    print("删除现有表...")
    Base.metadata.drop_all(engine)
    
    # 创建所有表
    print("创建新表...")
    Base.metadata.create_all(engine)
    
    # 创建会话
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 检查是否已存在admin用户
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("Admin用户已存在")
        else:
            # 创建admin用户
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password_hash=get_password_hash("admin123"),  # 使用password_hash字段
                status=UserStatusEnum.ACTIVE,
                role=UserRoleEnum.ADMIN,
                notification_preferences={
                    "email": True,
                    "push": True,
                    "sms": False
                },
                config={}
            )
            db.add(admin_user)
            db.commit()
            print("成功创建admin用户")
            
    except Exception as e:
        print(f"创建用户时出错: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()