#!/usr/bin/env python3
"""
详细测试500错误端点
"""

import requests
import json

BASE_URL = "http://localhost:8001"
LOGIN_ENDPOINT = "/api/auth/login"
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "admin123"
TIMEOUT = 10

def get_token():
    """获取JWT令牌"""
    login_url = BASE_URL + LOGIN_ENDPOINT
    payload = {
        "username": LOGIN_USERNAME,
        "password": LOGIN_PASSWORD
    }
    
    try:
        response = requests.post(login_url, json=payload, timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "access_token" in data["data"]:
                token = data["data"]["access_token"]
            elif "access_token" in data:
                token = data["access_token"]
            else:
                print("令牌未找到")
                return None
            
            return token
        else:
            print(f"登录失败，状态码: {response.status_code}")
            print(f"响应: {response.text[:500]}")
    except Exception as e:
        print(f"登录请求异常: {e}")
    
    return None

def test_endpoint_detailed(endpoint, token, path_params=None):
    """详细测试单个端点"""
    url = BASE_URL + endpoint
    
    # 替换路径参数
    if path_params:
        for key, value in path_params.items():
            placeholder = f"{{{key}}}"
            if placeholder in url:
                url = url.replace(placeholder, str(value))
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n{'='*80}")
    print(f"测试端点: {endpoint}")
    print(f"完整URL: {url}")
    print(f"路径参数: {path_params}")
    print(f"{'='*80}")
    
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        print(f"状态码: {response.status_code}")
        print(f"响应头:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        print(f"\n响应内容:")
        if response.text:
            try:
                data = response.json()
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except:
                print(response.text[:1000])
        else:
            print("(空响应)")
            
    except Exception as e:
        print(f"请求异常: {e}")

def main():
    print("详细测试500错误端点")
    
    # 获取令牌
    token = get_token()
    if not token:
        print("无法获取令牌")
        return
    
    print("令牌获取成功")
    
    # 测试有问题的端点
    problem_endpoints = [
        ("/api/v1/admin/crawler/headers/{header_id}", {"header_id": 1}),
        ("/api/v1/admin/headers/{header_id}", {"header_id": 1}),
        ("/api/v1/admin/ip-pools/{pool_id}", {"pool_id": 1}),
        ("/api/v1/admin/users/admin/{admin_id}", {"admin_id": 1}),
    ]
    
    for endpoint, params in problem_endpoints:
        test_endpoint_detailed(endpoint, token, params)
    
    print(f"\n{'='*80}")
    print("测试完成")

if __name__ == "__main__":
    main()