#!/usr/bin/env python3
"""
详细调试登录500错误
"""
import sys
import json
import requests
from pprint import pprint
import traceback

# 配置
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"

def test_login():
    print("=== 详细调试登录 ===")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print(f"发送POST请求到 {LOGIN_URL}")
    print(f"请求体: {json.dumps(login_data, indent=2)}")
    
    try:
        resp = requests.post(LOGIN_URL, json=login_data, timeout=10)
        print(f"\n状态码: {resp.status_code}")
        print(f"响应头:")
        for key, value in resp.headers.items():
            print(f"  {key}: {value}")
        
        print(f"\n响应体 (原始):")
        print(resp.text)
        
        # 尝试解析JSON
        try:
            data = resp.json()
            print(f"\n解析后的JSON:")
            pprint(data)
        except:
            pass
            
        # 如果是500错误，尝试获取更多信息
        if resp.status_code == 500:
            print("\n=== 500错误分析 ===")
            # 检查响应中是否有异常详情
            if "detail" in resp.text.lower() or "traceback" in resp.text.lower():
                print("响应中可能包含错误详情")
            
            # 尝试获取健康检查端点
            health_url = f"{BASE_URL}/api/v1/health"
            try:
                health_resp = requests.get(health_url, timeout=5)
                print(f"健康检查: {health_resp.status_code} - {health_resp.text}")
            except:
                print("健康检查失败")
                
    except Exception as e:
        print(f"请求异常: {e}")
        traceback.print_exc()

def test_with_headers():
    """测试带有自定义头部的请求"""
    print("\n=== 测试带有自定义头部的请求 ===")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "DebugScript/1.0"
    }
    
    try:
        resp = requests.post(LOGIN_URL, json=login_data, headers=headers, timeout=10)
        print(f"状态码: {resp.status_code}")
        print(f"响应体: {resp.text[:500]}")
    except Exception as e:
        print(f"错误: {e}")

def test_direct_db():
    """测试直接数据库操作"""
    print("\n=== 测试直接数据库操作 ===")
    try:
        import sys
        sys.path.insert(0, '.')
        from backend.core.database import SessionLocal
        from backend.models.admin_user import AdminUser
        from backend.core.security import verify_password
        
        session = SessionLocal()
        admin = session.query(AdminUser).filter(AdminUser.username == 'admin').first()
        print(f"找到admin用户: {admin.username}")
        print(f"密码哈希验证: {verify_password('admin123', admin.password_hash)}")
        
        # 测试user_activity_logger
        from backend.services.user_activity_logger import get_user_activity_logger
        logger = get_user_activity_logger(session)
        print(f"用户活动日志记录器创建成功: {logger}")
        
        # 尝试记录登录事件
        try:
            logger.log_user_login(
                user_id=admin.id,
                username=admin.username,
                ip_address="127.0.0.1",
                user_agent="DebugScript",
                success=True
            )
            print("成功记录登录事件")
        except Exception as e:
            print(f"记录登录事件失败: {e}")
            traceback.print_exc()
            
        session.close()
    except Exception as e:
        print(f"数据库测试失败: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_login()
    test_with_headers()
    test_direct_db()