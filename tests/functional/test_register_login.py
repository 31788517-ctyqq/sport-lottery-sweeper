import requests
import json
import sys

BASE = "http://localhost:8000/api/v1"

def register():
    url = f"{BASE}/auth/register"
    data = {
        "username": "admin",
        "email": "admin@example.com",
        "password": "admin123",
        "full_name": "系统管理员"
    }
    try:
        resp = requests.post(url, json=data, timeout=10)
        print(f"注册响应: {resp.status_code}")
        print(resp.text)
        return resp.status_code == 200
    except Exception as e:
        print(f"注册错误: {e}")
        return False

def login():
    url = f"{BASE}/auth/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    try:
        resp = requests.post(url, json=data, timeout=10)
        print(f"\n登录响应: {resp.status_code}")
        if resp.status_code == 200:
            result = resp.json()
            print(f"登录成功!")
            print(f"code: {result.get('code')}")
            print(f"message: {result.get('message')}")
            data = result.get('data', {})
            print(f"access_token: {data.get('access_token', 'N/A')}")
            print(f"user_info: {data.get('user_info', {})}")
            return True
        else:
            print(f"响应: {resp.text}")
            return False
    except Exception as e:
        print(f"登录错误: {e}")
        return False

if __name__ == "__main__":
    print("尝试注册admin用户...")
    if register():
        print("注册成功，现在测试登录...")
        if login():
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        print("注册失败")
        sys.exit(1)