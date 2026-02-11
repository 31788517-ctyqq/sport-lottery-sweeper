#!/usr/bin/env python3
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def import_all_models():
    """导入所有模型以确保它们被注册到Base.metadata"""
    from backend.models.admin_user import AdminUser
    from backend.models.department import Department
    from backend.models.llm_provider import LLMProvider
    from backend.models.data_sources import DataSource
    from backend.models.crawler_config import CrawlerConfig
    # 导入其他必要的模型
    from backend.models.user import User
    
    print("✅ 所有模型已成功导入")

def create_tables():
    """创建所有数据库表"""
    from backend.models.base import Base
    from backend.database import engine
    
    print("正在创建数据库表...")
    try:
        # 删除现有数据库文件（可选，用于干净启动）
        # import os
        # if os.path.exists("sport_lottery.db"):
        #     os.remove("sport_lottery.db")
        
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建成功")
        return True
    except Exception as e:
        print(f"❌ 数据库表创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_tables():
    """验证表是否已创建"""
    import sqlite3
    conn = sqlite3.connect('sport_lottery.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_users'")
    result = cursor.fetchone()
    conn.close()
    
    if result:
        print("✅ admin_users 表已成功创建")
        return True
    else:
        print("❌ admin_users 表未找到")
        return False

def create_initial_admin_user():
    """创建初始管理员用户"""
    from backend.database import engine
    from sqlalchemy.orm import sessionmaker
    from backend.models.admin_user import AdminUser, AdminRoleEnum, AdminStatusEnum
    from backend.core.security import get_password_hash
    
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
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=== 数据库表创建工具 (修正版) ===")
    import_all_models()
    if create_tables():
        if verify_tables():
            create_initial_admin_user()
    print("=== 完成 ===")