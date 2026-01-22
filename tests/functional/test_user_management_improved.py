"""
改进的用户管理模块测试脚本
用于测试前后端的用户注册与登录流程
"""
import asyncio
import requests
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import subprocess
import sys

from backend.config import settings
from backend.models.user import User
from backend.models.admin_user import AdminUser
from backend.core.security import get_password_hash
from backend.database import get_db


def check_user_model_consistency():
    """检查用户模型中字段的一致性问题"""
    print("🔍 检查用户模型字段一致性...")
    
    from backend.models.user import User
    from sqlalchemy import inspect
    
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    columns = inspector.get_columns('users')
    column_names = [col['name'] for col in columns]
    
    print(f"   用户表字段: {column_names}")
    
    if 'password_hash' in column_names and 'hashed_password' not in column_names:
        print("   ✅ 用户模型字段一致性检查通过")
        return True
    else:
        print("   ❌ 用户模型字段一致性检查失败")
        return False


def create_test_user():
    """创建测试普通用户"""
    print("\n🔑 创建测试普通用户...")
    
    try:
        # 使用数据库会话创建测试用户
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # 检查是否已存在测试用户
        existing_user = db.query(User).filter(User.username == "test_user").first()
        if existing_user:
            print("   ℹ️  测试普通用户已存在")
            return True
        
        # 创建测试普通用户
        from backend.models.user import UserStatusEnum, UserTypeEnum, UserRoleEnum
        from backend.core.security import get_password_hash
        
        password_hash = get_password_hash("testpassword123")
        test_user = User(
            username="test_user",
            email="test_user@example.com",
            password_hash=password_hash,
            first_name="Test",
            last_name="User",
            nickname="test_nick",
            bio="A test user account",
            phone="+1234567890",
            country="CN",
            city="Beijing",
            role=UserRoleEnum.REGULAR_USER,
            status=UserStatusEnum.ACTIVE,
            is_verified=True,
            user_type=UserTypeEnum.NORMAL,
            timezone="Asia/Shanghai",
            language="zh-CN"
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"   ✅ 测试普通用户创建成功: {test_user.username}")
        return True
        
    except Exception as e:
        print(f"   ❌ 创建测试普通用户失败: {str(e)}")
        return False
    finally:
        db.close()


def test_user_authentication():
    """测试用户认证功能"""
    print("\n🔐 测试用户认证功能...")
    
    try:
        # 测试认证服务
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from backend.services.auth_service import AuthenticationService
        
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            auth_service = AuthenticationService(db)
            
            # 测试用户认证
            user = asyncio.run(auth_service.authenticate_user("test_user", "testpassword123"))
            if user:
                print(f"   ✅ 用户认证成功: {user.username}")
                
                # 测试获取用户信息
                fetched_user = auth_service.get_user_by_email("test_user@example.com")
                if fetched_user:
                    print(f"   ✅ 用户信息获取成功: {fetched_user.username}")
                    return True
                else:
                    print("   ❌ 用户信息获取失败")
                    return False
            else:
                print("   ❌ 用户认证失败")
                return False
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"   ❌ 用户认证测试失败: {str(e)}")
        return False


def check_backend_routes():
    """检查后端API路由"""
    print("\n🌐 检查后端API路由...")
    
    try:
        # 检查路由是否注册
        from backend.main import app
        routes = [route.path for route in app.routes]
        
        auth_routes = [route for route in routes if '/api/v1/auth' in route]
        if auth_routes:
            print(f"   ✅ 发现已注册的认证路由: {auth_routes}")
            return True
        else:
            print("   ❌ 未找到认证相关路由")
            return False
            
    except Exception as e:
        print(f"   ❌ 检查路由失败: {str(e)}")
        return False


def run_comprehensive_test():
    """运行综合测试"""
    print("🚀 开始测试项目用户管理模块")
    print("="*60)
    
    # 1. 检查模型字段一致性
    consistency_ok = check_user_model_consistency()
    
    # 2. 创建测试用户
    user_created = create_test_user()
    
    # 3. 测试用户认证
    auth_works = test_user_authentication()
    
    # 4. 检查API路由
    routes_ok = check_backend_routes()
    
    print("\n" + "="*60)
    print("📋 测试结果汇总:")
    
    tests = [
        ("字段一致性检查", consistency_ok),
        ("测试用户创建", user_created),
        ("用户认证功能", auth_works),
        ("API路由检查", routes_ok)
    ]
    
    passed_tests = 0
    for test_name, result in tests:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\n📊 总体结果: {passed_tests}/{len(tests)} 项测试通过")
    
    if passed_tests == len(tests):
        print("🎉 用户管理模块测试全部通过!")
        return True
    else:
        print("⚠️  存在测试失败，请检查上述错误信息并修复")
        return False


def start_backend_service():
    """启动后端服务的提示"""
    print("\n🔧 如需测试API端点，请按以下步骤启动后端服务:")
    print("   1. 确保已安装依赖: pip install -r requirements.txt")
    print("   2. 启动后端服务: uvicorn backend.main:app --reload --port 8000")
    print("   3. 在浏览器访问: http://localhost:8000/api/v1/auth/register")
    print("   4. 使用API工具测试注册和登录功能")


if __name__ == "__main__":
    run_comprehensive_test()
    start_backend_service()