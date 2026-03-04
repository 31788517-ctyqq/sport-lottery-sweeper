#!/usr/bin/env python3
"""
数据库初始化脚本
创建表结构并插入初始数据
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# 添加backend到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from database_utils import engine, Base
from .models.user import User, UserRole, UserStatus, SocialProvider
from .models.admin_user import AdminUser, AdminRoleEnum, AdminStatusEnum
from models.system_config import SystemConfig
from core.security import get_password_hash

def create_tables():
    """创建所有数据库表"""
    print("正在创建数据库表...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建成功")
        return True
    except Exception as e:
        print(f"❌ 数据库表创建失败: {e}")
        return False

def create_initial_data():
    """创建初始数据"""
    print("正在创建初始数据...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 创建超级管理员用户
        admin_user = AdminUser(
            username="superadmin",
            email="admin@sportlottery.com",
            hashed_password=get_password_hash("Admin123456!"),
            full_name="超级管理员",
            role=AdminRoleEnum.SUPER_ADMIN,
            status=AdminStatusEnum.ACTIVE,
            phone="13800138000",
            department="技术部"
        )
        
        # 检查是否已存在
        existing_admin = db.query(AdminUser).filter(AdminUser.username == "superadmin").first()
        if not existing_admin:
            db.add(admin_user)
            print("✅ 创建超级管理员用户: superadmin")
        
        # 创建普通管理员用户
        normal_admin = AdminUser(
            username="admin",
            email="normal@sportlottery.com",
            hashed_password=get_password_hash("Admin123456!"),
            full_name="普通管理员",
            role=AdminRoleEnum.ADMIN,
            status=AdminStatusEnum.ACTIVE,
            phone="13800138001",
            department="运营部"
        )
        
        existing_normal = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not existing_normal:
            db.add(normal_admin)
            print("✅ 创建普通管理员用户: admin")
        
        # 创建系统配置
        configs = [
            SystemConfig(
                config_key="system_name",
                config_value="竞彩足球扫盘系统",
                description="系统名称",
                config_type="string",
                is_public=True
            ),
            SystemConfig(
                config_key="max_login_attempts",
                config_value="5",
                description="最大登录尝试次数",
                config_type="integer",
                is_public=False
            ),
            SystemConfig(
                config_key="session_timeout",
                config_value="3600",
                description="会话超时时间（秒）",
                config_type="integer",
                is_public=False
            ),
            SystemConfig(
                config_key="crawler_interval",
                config_value="300",
                description="爬虫采集间隔（秒）",
                config_type="integer",
                is_public=False
            ),
            SystemConfig(
                config_key="prediction_enabled",
                config_value="true",
                description="是否启用预测功能",
                config_type="boolean",
                is_public=True
            )
        ]
        
        for config in configs:
            existing_config = db.query(SystemConfig).filter(SystemConfig.config_key == config.config_key).first()
            if not existing_config:
                db.add(config)
        
        print("✅ 创建系统配置")
        
        # 创建演示用户
        demo_user = User(
            username="demo",
            email="demo@sportlottery.com",
            hashed_password=get_password_hash("Demo123456!"),
            nickname="演示用户",
            phone="13800138002",
            status=UserStatusEnum.ACTIVE,
            user_type="free"
        )
        
        existing_demo = db.query(User).filter(User.username == "demo").first()
        if not existing_demo:
            db.add(demo_user)
            print("✅ 创建演示用户: demo")
        
        db.commit()
        print("✅ 初始数据创建成功")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 初始数据创建失败: {e}")
        return False
    finally:
        db.close()
    
    return True

def test_database_connection():
    """测试数据库连接"""
    print("测试数据库连接...")
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ 数据库连接正常")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始初始化数据库...\n")
    
    # 测试连接
    if not test_database_connection():
        print("\n请检查数据库配置后重试")
        return False
    
    # 创建表
    if not create_tables():
        return False
    
    # 创建初始数据
    if not create_initial_data():
        return False
    
    print("\n🎉 数据库初始化完成！")
    print("\n默认登录账号:")
    print("  超级管理员: superadmin / Admin123456!")
    print("  普通管理员: admin / Admin123456!")
    print("  演示用户: demo / Demo123456!")
    
    return True

if __name__ == "__main__":
    main()