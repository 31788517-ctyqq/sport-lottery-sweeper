#!/usr/bin/env python3
import requests
import json

def test_login():
    url = "http://localhost:8000/api/v1/login"
    payload = {
        "username": "admin",
        "password": "admin123"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 登录成功！")
            return True
        else:
            print("❌ 登录失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

if __name__ == "__main__":
    test_login()