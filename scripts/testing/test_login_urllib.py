#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json

def test_login_urllib():
    url = "http://localhost:8000/api/v1/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    # 转换为JSON
    json_data = json.dumps(data).encode('utf-8')
    
    # 创建请求
    req = urllib.request.Request(url, data=json_data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"Status: {response.status}")
            print(f"Response: {result}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(f"Response: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login_urllib()