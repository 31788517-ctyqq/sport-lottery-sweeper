"""
用户管理模块测试脚本
用于测试前后端的用户注册与登录流程
"""
import asyncio
import requests
import json
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.config import settings
from backend.models.user import User
from backend.models.admin_user import AdminUser
from backend.core.security import get_password_hash
from backend.database import get_db


def check_user_model_consistency():
    """检查用户模型中字段的一致性问题"""
    print("\n[INSPECT] 检查用户模型字段一致性...")
    
    engine = create_engine(settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://'))
    inspector = inspect(engine)
    
    columns = inspector.get_columns('users')
    column_names = [col['name'] for col in columns]
    
    print(f"   用户表字段: {column_names}")
    
    if 'password_hash' in column_names and 'hashed_password' not in column_names:
        print("   [ERROR] 发现字段不一致: 模型中使用password_hash，但服务中使用hashed_password")
        print("   需要修复: auth_service.py中的hashed_password应改为password_hash")
        return False
    else:
        print("   [OK] 字段一致性检查通过")
        return True


def fix_auth_service_field_names():
    """修复认证服务中的字段名错误"""
    print("\n[FIX] 修复认证服务中的字段名错误...")
    
    auth_service_path = "backend/services/auth_service.py"
    
    # 检查文件是否存在
    if not os.path.exists(auth_service_path):
        print(f"   [ERROR] 文件不存在: {auth_service_path}")
        return False
    
    # 读取文件
    with open(auth_service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换字段名
    fixed_content = content.replace('hashed_password', 'password_hash')
    
    # 检查是否进行了替换
    if content != fixed_content:
        with open(auth_service_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print("   [OK] 已修复 auth_service.py 中的字段名错误")
        return True
    else:
        print("   ℹ️  未发现需要修复的字段名错误")
        return True


def create_test_admin_user():
    """创建测试管理员用户"""
    print("\n[KEY] 创建测试管理员用户...")
    
    try:
        # 使用数据库会话创建测试用户
        engine = create_engine(settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://'))
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # 检查是否已存在测试用户
        existing_user = db.query(AdminUser).filter(AdminUser.username == "test_admin").first()
        if existing_user:
            print("   ℹ️  测试管理员用户已存在")
            return True
        
        # 创建测试管理员用户
        from backend.models.admin_user import AdminRoleEnum, AdminStatusEnum
        
        hashed_password = get_password_hash("testpassword123")
        test_admin = AdminUser(
            username="test_admin",
            email="test_admin@example.com",
            password_hash=hashed_password,
            real_name="Test Administrator",
            phone="+1234567890",
            department="Testing",
            position="QA",
            role=AdminRoleEnum.ADMIN,
            status=AdminStatusEnum.ACTIVE,
            is_verified=True
        )
        
        db.add(test_admin)
        db.commit()
        db.refresh(test_admin)
        
        print(f"   [OK] 测试管理员用户创建成功: {test_admin.username}")
        return True
        
    except Exception as e:
        print(f"   [ERROR] 创建测试管理员用户失败: {str(e)}")
        return False
    finally:
        db.close()


def test_backend_user_registration():
    """测试后端用户注册功能"""
    print("\n[TEST] 开始测试后端用户注册功能...")
    
    # 确定后端URL
    backend_url = settings.BACKEND_CORS_ORIGINS[0] if settings.BACKEND_CORS_ORIGINS else 'http://localhost:8000'
    register_url = f"{backend_url}/api/v1/auth/register"
    
    # 准备测试数据
    timestamp = int(datetime.now().timestamp())
    test_user_data = {
        "username": f"test_user_{timestamp}",
        "email": f"test{timestamp}@example.com",
        "password": "securepassword123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(register_url, json=test_user_data)
        print(f"[OK] 注册响应: {response.status_code}")
        print(f"   响应内容: {response.json()}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("   [OK] 注册测试成功")
            return True
        else:
            print(f"   [WARNING]  注册未返回成功状态码")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   [ERROR] 无法连接到后端服务，请确保服务正在运行")
        print(f"      尝试访问的URL: {register_url}")
        print(f"      提示: 运行 'uvicorn backend.main:app --reload --port 8000' 启动服务")
        return False
    except Exception as e:
        print(f"[ERROR] 注册测试失败: {str(e)}")
        return False


def test_backend_user_login():
    """测试后端用户登录功能"""
    print("\n[TEST] 开始测试后端用户登录功能...")
    
    # 确定后端URL
    backend_url = settings.BACKEND_CORS_ORIGINS[0] if settings.BACKEND_CORS_ORIGINS else 'http://localhost:8000'
    login_url = f"{backend_url}/api/v1/auth/login"
    
    # 使用已知的管理员账户进行测试
    login_data = {
        "username": "admin",
        "password": "admin123"  # 可能需要根据实际情况调整
    }
    
    try:
        response = requests.post(login_url, data=login_data)  # 注意：登录通常使用表单数据而非JSON
        print(f"[OK] 登录响应: {response.status_code}")
        if response.status_code == 200:
            print(f"   登录成功: {response.json()}")
            return True
        else:
            print(f"   登录失败: {response.json()}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   [ERROR] 无法连接到后端服务，请确保服务正在运行")
        print(f"      尝试访问的URL: {login_url}")
        print(f"      提示: 运行 'uvicorn backend.main:app --reload --port 8000' 启动服务")
        return False
    except Exception as e:
        print(f"[ERROR] 登录测试失败: {str(e)}")
        return False


def run_comprehensive_test():
    """运行综合测试"""
    print("[ROCKET] 开始测试项目用户管理模块")
    print("="*60)
    
    results = []
    
    # 1. 检查模型字段一致性
    consistency_ok = check_user_model_consistency()
    results.append(("字段一致性检查", consistency_ok))
    
    # 2. 修复字段名错误（如果需要）
    if not consistency_ok:
        fix_ok = fix_auth_service_field_names()
        results.append(("字段名修复", fix_ok))
        # 再次检查修复后的一致性
        consistency_ok = check_user_model_consistency()
        results.append(("修复后一致性检查", consistency_ok))
    
    # 3. 创建测试管理员用户
    admin_created = create_test_admin_user()
    results.append(("测试管理员用户创建", admin_created))
    
    # 4. 测试注册和登录功能
    print("\n[NOTE] API功能测试说明:")
    print("- 要完整测试注册和登录功能，需要先启动后端服务")
    print("- 启动后端服务命令: uvicorn backend.main:app --reload --port 8000")
    print("- 然后再运行此测试脚本来验证API功能")
    
    reg_tested = test_backend_user_registration()
    results.append(("用户注册测试", reg_tested))
    
    login_tested = test_backend_user_login()
    results.append(("用户登录测试", login_tested))
    
    # 输出最终结果
    print("\n" + "="*60)
    print("[LOG] 测试结果汇总:")
    total_passed = 0
    for test_name, result in results:
        status = "[OK] 通过" if result else "[ERROR] 失败"
        if result:
            total_passed += 1
        print(f"   - {test_name}: {status}")
    
    print(f"\n[ANALYTICS] 总体结果: {total_passed}/{len(results)} 项测试通过")
    
    if all(result for _, result in results):
        print("[SUCCESS] 所有测试均成功完成！")
        return True
    else:
        print("[WARNING]  存在测试失败，请检查上述错误信息并修复")
        return False


if __name__ == "__main__":
    run_comprehensive_test()
