#!/usr/bin/env python3
"""
测试不同路径格式
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_path(path):
    url = f"{BASE_URL}{path}"
    try:
        response = requests.get(url, timeout=5)
        print(f"测试 {url}:")
        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"  响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        elif response.status_code == 401:
            print(f"  需要认证: {response.text}")
        else:
            print(f"  错误: {response.text}")
        print()
        return response.status_code
    except Exception as e:
        print(f"测试 {url}:")
        print(f"  异常: {e}")
        print()
        return 0

print("测试LLM供应商路径...")
print("=" * 50)

# 测试不同路径格式
paths = [
    "/api/v1/llm-providers",
    "/api/v1/llm-providers/",
    "/api/v1/llm-providers?skip=0&limit=10",
    "/api/v1/llm-providers/count",
    "/api/v1/llm-providers/stats/overview",
]

for path in paths:
    test_path(path)

# 测试需要认证的端点 - 尝试使用管理员令牌
print("\n测试需要认证的端点...")
print("=" * 50)

# 先登录获取令牌
login_url = f"{BASE_URL}/api/v1/auth/login"
login_data = {
    "username": "admin",
    "password": "admin123"
}
try:
    login_response = requests.post(login_url, json=login_data, timeout=5)
    if login_response.status_code == 200:
        login_result = login_response.json()
        token = None
        if "data" in login_result and "access_token" in login_result["data"]:
            token = login_result["data"]["access_token"]
        elif "access_token" in login_result:
            token = login_result["access_token"]
        
        if token:
            print(f"登录成功，获取到令牌")
            headers = {"Authorization": f"Bearer {token}"}
            
            # 使用令牌测试端点
            test_path_with_auth = f"{BASE_URL}/api/v1/llm-providers"
            response = requests.get(test_path_with_auth, headers=headers, timeout=5)
            print(f"使用令牌测试 {test_path_with_auth}:")
            print(f"  状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  响应记录数: {len(data) if isinstance(data, list) else 'N/A'}")
                print(f"  响应类型: {type(data)}")
            else:
                print(f"  错误: {response.text}")
        else:
            print("登录成功但未找到令牌")
    else:
        print(f"登录失败: {login_response.status_code} - {login_response.text}")
except Exception as e:
    print(f"登录测试异常: {e}")