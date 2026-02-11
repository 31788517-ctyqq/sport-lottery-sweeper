#!/usr/bin/env python3
"""
测试北单比赛端点
"""
import requests
import json
import traceback
import sys

BASE_URL = "http://localhost:8000"
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
        traceback.print_exc()
    return None

def test_beidan():
    token = get_token()
    if not token:
        print("无法获取令牌")
        sys.exit(1)
    
    url = BASE_URL + "/api/v1/admin/matches/beidan/matches"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"测试端点: {url}")
    print(f"令牌长度: {len(token)}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("成功响应:")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
        elif response.status_code == 500:
            print("500 内部服务器错误:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print("原始响应文本:")
                print(response.text[:2000])
        else:
            print("响应文本:")
            print(response.text[:1000])
            
    except requests.exceptions.Timeout:
        print("请求超时 (30秒)")
    except Exception as e:
        print(f"请求异常: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_beidan()