#!/usr/bin/env python3
"""
竞彩足球扫盘系统 - 完整功能测试脚本
验证数据模型、API接口和核心功能
"""

import sys
import os
import time
import requests
import json
from datetime import datetime

# 添加backend到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_database_models():
    """测试数据库模型导入"""
    print("[TEST] 测试数据库模型导入...")
    try:
        from models.user import User, UserRoleEnum, UserStatusEnum
        from models.admin_user import AdminUser, AdminRoleEnum, AdminStatusEnum
        from models.match import Match, Team, League
        from models.intelligence import Intelligence, IntelligenceTypeEnum
        from models.predictions import Prediction, PredictionTypeEnum
        from models.odds import Odds, OddsTypeEnum
        from models.data_review import DataReview, ReviewStatusEnum
        from models.sp_records import SPRecord
        from models.draw_prediction_result import DrawPredictionResult
        
        print("  [OK] 所有数据模型导入成功")
        print(f"     - 用户模型: User, AdminUser")
        print(f"     - 比赛模型: Match, Team, League")
        print(f"     - 情报模型: Intelligence")
        print(f"     - 预测模型: Prediction, DrawPredictionResult")
        print(f"     - 赔率模型: Odds")
        print(f"     - 审核模型: DataReview")
        print(f"     - SP管理模型: SPRecord")
        return True
    except Exception as e:
        print(f"  [ERROR] 模型导入失败: {e}")
        return False

def test_security_functions():
    """测试安全工具函数"""
    print("\n[TEST] 测试安全工具函数...")
    try:
        from core.security import (
            get_password_hash, verify_password, 
            create_access_token, validate_password_strength
        )
        
        # 测试密码哈希
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        verified = verify_password(password, hashed)
        
        if not verified:
            print("  [ERROR] 密码验证失败")
            return False
        print("  [OK] 密码哈希和验证正常")
        
        # 测试JWT令牌
        token = create_access_token({"sub": "test_user", "role": "user"})
        if not token or len(token.split('.')) != 3:
            print("  [ERROR] JWT令牌生成失败")
            return False
        print("  [OK] JWT令牌生成正常")
        
        # 测试密码强度
        weak_password = "123"
        strong_password = "MyStrongP@ssw0rd123!"
        weak_result = validate_password_strength(weak_password)
        strong_result = validate_password_strength(strong_password)
        
        if weak_result['valid'] or not strong_result['valid']:
            print("  [ERROR] 密码强度验证异常")
            return False
        print("  [OK] 密码强度验证正常")
        
        return True
    except Exception as e:
        print(f"  [ERROR] 安全函数测试失败: {e}")
        return False

def test_database_connection():
    """测试数据库连接"""
    print("\n[TEST] 测试数据库连接...")
    try:
        from database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.scalar() == 1:
                print("  [OK] 数据库连接正常")
                return True
            else:
                print("  [ERROR] 数据库查询异常")
                return False
    except Exception as e:
        print(f"  [ERROR] 数据库连接失败: {e}")
        print("     [HINT] 提示: 请确保PostgreSQL服务正在运行")
        return False

def test_api_health():
    """测试API健康状态"""
    print("\n[TEST] 测试API健康状态...")
    
    # 等待服务启动
    print("  ⏳ 等待后端服务启动...")
    time.sleep(3)
    
    try:
        # 测试健康检查端点
        response = requests.get("http://localhost:8001/health", timeout=10)
        if response.status_code == 200:
            print("  [OK] API健康检查通过")
            return True
        else:
            print(f"  [ERROR] API健康检查失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  [ERROR] 无法连接到API服务 (http://localhost:8001)")
        print("     [HINT] 提示: 请先启动后端服务: cd backend && python -m uvicorn main:app --reload")
        return False
    except requests.exceptions.Timeout:
        print("  [ERROR] API响应超时")
        return False
    except Exception as e:
        print(f"  [ERROR] API测试异常: {e}")
        return False

def test_api_documentation():
    """测试API文档"""
    print("\n[TEST] 测试API文档...")
    try:
        # 测试Swagger文档
        response = requests.get("http://localhost:8001/docs", timeout=10)
        if response.status_code == 200:
            print("  [OK] Swagger API文档可访问")
        else:
            print(f"  [WARNING]  Swagger文档访问异常: HTTP {response.status_code}")
        
        # 测试ReDoc文档
        response = requests.get("http://localhost:8001/redoc", timeout=10)
        if response.status_code == 200:
            print("  [OK] ReDoc API文档可访问")
        else:
            print(f"  [WARNING]  ReDoc文档访问异常: HTTP {response.status_code}")
        
        return True
    except Exception as e:
        print(f"  [WARNING]  API文档测试异常: {e}")
        return False

def test_model_relationships():
    """测试模型关系"""
    print("\n[TEST] 测试模型关系定义...")
    try:
        from models.user import User
        from models.admin_user import AdminUser
        from models.match import Match
        from sqlalchemy import inspect
        
        # 检查User模型的表名
        inspector = inspect(User)
        table_name = inspector.local_table.name
        if table_name != 'users':
            print(f"  [ERROR] User模型表名错误: {table_name}")
            return False
        print("  [OK] User模型表名正确: users")
        
        # 检查AdminUser模型的表名
        inspector = inspect(AdminUser)
        table_name = inspector.local_table.name
        if table_name != 'admin_users':
            print(f"  [ERROR] AdminUser模型表名错误: {table_name}")
            return False
        print("  [OK] AdminUser模型表名正确: admin_users")
        
        # 检查Match模型的表名
        inspector = inspect(Match)
        table_name = inspector.local_table.name
        if table_name != 'matches':
            print(f"  [ERROR] Match模型表名错误: {table_name}")
            return False
        print("  [OK] Match模型表名正确: matches")
        
        print("  [OK] 所有模型表名定义正确")
        return True
    except Exception as e:
        print(f"  [ERROR] 模型关系测试失败: {e}")
        return False

def test_enum_values():
    """测试枚举值"""
    print("\n[TEST] 测试枚举值定义...")
    try:
        from models.user import UserStatusEnum, UserTypeEnum
        from models.admin_user import AdminRoleEnum, AdminStatusEnum
        from models.match import MatchStatusEnum, MatchTypeEnum
        from models.predictions import PredictionTypeEnum
        from models.odds import OddsTypeEnum
        
        # 测试用户状态枚举
        statuses = [status.value for status in UserStatusEnum]
        expected_statuses = ["active", "inactive", "suspended", "pending"]
        if set(statuses) != set(expected_statuses):
            print(f"  [ERROR] 用户状态枚举错误: {statuses}")
            return False
        print(f"  [OK] 用户状态枚举正确: {statuses}")
        
        # 测试管理员角色枚举
        roles = [role.value for role in AdminRoleEnum]
        expected_roles = ["super_admin", "admin", "operator", "analyst"]
        if set(roles) != set(expected_roles):
            print(f"  [ERROR] 管理员角色枚举错误: {roles}")
            return False
        print(f"  [OK] 管理员角色枚举正确: {roles}")
        
        # 测试比赛状态枚举
        match_statuses = [status.value for status in MatchStatusEnum]
        print(f"  [OK] 比赛状态枚举: {match_statuses}")
        
        print("  [OK] 所有枚举值定义正确")
        return True
    except Exception as e:
        print(f"  [ERROR] 枚举值测试失败: {e}")
        return False

def print_summary(results):
    """打印测试结果摘要"""
    print("\n" + "="*60)
    print("[ANALYTICS] 系统测试摘要")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    failed_tests = total_tests - passed_tests
    
    print(f"总测试项: {total_tests}")
    print(f"[OK] 通过: {passed_tests}")
    print(f"[ERROR] 失败: {failed_tests}")
    print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\n详细结果:")
    for test_name, result in results.items():
        status = "[OK] 通过" if result else "[ERROR] 失败"
        print(f"  {status}: {test_name}")
    
    print("\n" + "="*60)
    
    if failed_tests == 0:
        print("[SUCCESS] 恭喜！所有测试通过，系统准备就绪！")
        print("\n[ROCKET] 下一步操作建议:")
        print("  1. 运行 'python backend/init_db.py' 初始化数据库")
        print("  2. 启动完整开发环境: PowerShell -File start-dev.ps1")
        print("  3. 访问 http://localhost:8001/docs 查看API文档")
        print("  4. 使用默认账号登录: superadmin / Admin123456!")
    else:
        print("[WARNING]  部分测试失败，请根据提示修复问题后重试")
    
    print("="*60)

def main():
    """主测试函数"""
    print("[ROCKET] 竞彩足球扫盘系统 - 完整功能测试")
    print("测试时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    # 执行所有测试
    results = {
        "数据库模型导入": test_database_models(),
        "安全工具函数": test_security_functions(),
        "数据库连接": test_database_connection(),
        "模型关系定义": test_model_relationships(),
        "枚举值定义": test_enum_values(),
        "API健康状态": test_api_health(),
        "API文档访问": test_api_documentation()
    }
    
    # 打印摘要
    print_summary(results)
    
    # 返回退出码
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)