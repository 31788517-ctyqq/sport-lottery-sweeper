#!/usr/bin/env python3
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from backend.database import engine, Base
    from backend.models.admin_user import AdminUser
    from backend.core.security import get_password_hash
    from backend.models.admin_user import AdminRoleEnum, AdminStatusEnum
    from sqlalchemy.orm import sessionmaker
    
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建成功")
    
    # 创建初始管理员用户
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 检查是否已存在管理员用户
        existing_admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not existing_admin:
            admin_user = AdminUser(
                username="admin",
                email="admin@sportlottery.com",
                password_hash=get_password_hash("admin123"),
                real_name="系统管理员",
                role=AdminRoleEnum.ADMIN,
                status=AdminStatusEnum.ACTIVE
            )
            db.add(admin_user)
            db.commit()
            print("✅ 初始管理员用户创建成功 (用户名: admin, 密码: admin123)")
        else:
            print("ℹ️  管理员用户已存在")
            
    except Exception as e:
        print(f"❌ 创建初始用户失败: {e}")
        db.rollback()
    finally:
        db.close()
        
except Exception as e:
    print(f"❌ 数据库初始化失败: {e}")
    import traceback
    traceback.print_exc()