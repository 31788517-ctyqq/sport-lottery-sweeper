#!/usr/bin/env python3
import sys
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir
sys.path.insert(0, str(project_root))

import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.security import verify_password, get_password_hash
from backend.models.user import User, UserStatusEnum
from backend.models.admin_user import AdminUser, AdminStatusEnum

def test_user_authentication():
    print("=== 测试用户认证 ===")
    
    # 直接数据库连接
    db_path = "sport_lottery.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. 检查users表中的admin用户
    cursor.execute("SELECT * FROM users WHERE username='admin';")
    user_row = cursor.fetchone()
    
    if user_row:
        print(f"\n1. users表中的admin用户:")
        print(f"   ID: {user_row['id']}")
        print(f"   用户名: {user_row['username']}")
        print(f"   邮箱: {user_row['email']}")
        print(f"   密码哈希: {user_row['password_hash']}")
        print(f"   状态: {user_row['status']}")
        print(f"   角色: {user_row['role']}")
        print(f"   user_type: {user_row['user_type']}")
        
        # 验证密码
        test_password = "admin123"
        if verify_password(test_password, user_row['password_hash']):
            print(f"   ✓ 密码 '{test_password}' 验证成功")
        else:
            print(f"   ✗ 密码 '{test_password}' 验证失败")
            
        # 检查用户状态
        if user_row['status'] == 'active':
            print("   ✓ 用户状态为 active")
        else:
            print(f"   ✗ 用户状态为 {user_row['status']} (应为 active)")
            
        # 检查是否有必要的字段
        required_fields = ['username', 'password_hash', 'status']
        missing_fields = []
        for field in required_fields:
            if not user_row[field]:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"   ✗ 缺少必填字段: {missing_fields}")
        else:
            print("   ✓ 所有必填字段都存在")
    
    # 2. 检查admin_users表
    print("\n2. admin_users表:")
    cursor.execute("SELECT * FROM admin_users;")
    admin_rows = cursor.fetchall()
    
    if admin_rows:
        for admin in admin_rows:
            print(f"   用户名: {admin['username']}, 邮箱: {admin['email']}, 角色: {admin['role']}, 状态: {admin['status']}")
    else:
        print("   表为空")
    
    conn.close()
    
    # 3. 使用SQLAlchemy测试
    print("\n3. 使用SQLAlchemy测试:")
    try:
        engine = create_engine(f"sqlite:///{db_path}")
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 查询User模型
        user = session.query(User).filter(User.username == 'admin').first()
        if user:
            print(f"   ✓ 通过User模型找到admin用户")
            print(f"     密码哈希: {user.password_hash}")
            print(f"     状态: {user.status.value if hasattr(user.status, 'value') else user.status}")
            print(f"     角色: {user.role.value if hasattr(user.role, 'value') else user.role}")
            print(f"     用户类型: {user.user_type.value if hasattr(user.user_type, 'value') else user.user_type}")
            
            # 验证密码
            if verify_password("admin123", user.password_hash):
                print(f"     密码验证: 成功")
            else:
                print(f"     密码验证: 失败")
        else:
            print("   ✗ 通过User模型未找到admin用户")
            
        # 查询AdminUser模型
        admin_user = session.query(AdminUser).filter(AdminUser.username == 'admin').first()
        if admin_user:
            print(f"   ✓ 通过AdminUser模型找到admin用户")
        else:
            print("   ✗ 通过AdminUser模型未找到admin用户")
            
        session.close()
        
    except Exception as e:
        print(f"   SQLAlchemy错误: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_user_authentication()