"""
测试用户管理页面API端点是否正确注册
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from backend.main import app
from fastapi.testclient import TestClient

def test_api_routes():
    client = TestClient(app)
    
    # 首先检查应用是否能正常启动
    print("检查FastAPI应用是否正常...")
    
    # 测试根路径
    try:
        response = client.get("/")
        print(f"根路径状态: {response.status_code}")
    except Exception as e:
        print(f"根路径错误: {e}")
    
    # 检查API文档路径
    try:
        response = client.get("/docs")
        print(f"API文档状态: {response.status_code}")
    except Exception as e:
        print(f"API文档错误: {e}")
    
    # 尝试访问admin-users的路径，使用模拟token
    print("\n测试admin-users API端点...")
    
    # 生成一个有效的JWT令牌
    import jwt
    from datetime import datetime, timedelta
    from backend.config import settings
    
    payload = {
        "user_id": 1,
        "username": "admin",
        "role": "admin",
        "user_type": "admin",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 测试不同的路径
    test_paths = [
        "/api/v1/admin/admin-users",
        "/api/v1/admin/admin-users/",
        "/api/v1/admin/admin-users/current-user",
        "/api/v1/admin/admin-users/stats"
    ]
    
    for path in test_paths:
        try:
            response = client.get(path, headers=headers, params={"skip": 0, "limit": 10})
            print(f"{path}: {response.status_code}")
            if response.status_code == 500:
                print(f"  500错误详情: {response.text[:200]}")
            elif response.status_code == 422:
                print(f"  422错误: 参数验证失败")
            elif response.status_code == 404:
                print(f"  404错误: 路径未找到")
        except Exception as e:
            print(f"{path}: 错误 - {e}")
    
    # 测试不带认证的请求
    print("\n测试无认证访问...")
    try:
        response = client.get("/api/v1/admin/admin-users")
        print(f"无认证访问: {response.status_code}")
    except Exception as e:
        print(f"无认证访问错误: {e}")

if __name__ == "__main__":
    test_api_routes()