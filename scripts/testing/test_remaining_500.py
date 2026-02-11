#!/usr/bin/env python3
import requests
import sys

BASE_URL = "http://localhost:8001"
LOGIN_ENDPOINT = "/api/auth/login"
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "admin123"

def get_token():
    """获取JWT令牌"""
    login_url = BASE_URL + LOGIN_ENDPOINT
    payload = {
        "username": LOGIN_USERNAME,
        "password": LOGIN_PASSWORD
    }
    
    try:
        response = requests.post(login_url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "access_token" in data["data"]:
                token = data["data"]["access_token"]
                return token
            elif "access_token" in data:
                token = data["access_token"]
                return token
            else:
                print("令牌未找到，响应结构:", data.keys())
        else:
            print(f"登录失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"登录请求异常: {e}")
    return None

def test_endpoint(endpoint, token):
    """测试单个端点"""
    url = BASE_URL + endpoint
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"端点: {endpoint}")
        print(f"状态码: {response.status_code}")
        if response.status_code >= 400:
            print(f"响应: {response.text[:500]}")
        print("-" * 50)
        return response.status_code
    except Exception as e:
        print(f"请求异常: {e}")
        return None

def main():
    token = get_token()
    if not token:
        print("无法获取令牌，退出")
        sys.exit(1)
    
    endpoints = [
        "/api/v1/admin/options",
        "/api/v1/admin/stats",
        "/api/v1/admin/matches/beidan/matches",  # 之前已修复，验证是否正常
    ]
    
    print(f"令牌获取成功，测试{len(endpoints)}个端点...")
    
    for endpoint in endpoints:
        test_endpoint(endpoint, token)

if __name__ == "__main__":
    main()