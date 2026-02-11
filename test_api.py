import requests
import json

# 测试API
url = "http://localhost:8000/api/v1/data-source-100qiu/"

# 构造请求数据
data = {
    "name": "Test 100qiu",
    "url": "http://example.com",
    "date_time": "latest",
    "update_frequency": 60,
    "field_mapping": {},
    "status": "online"
}

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# 设置API基础URL
BASE_URL = "http://localhost:8000/api/v1/admin"

# 模拟一个管理员token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyNTA4ODQwMCwiYWRtaW5faWQiOjEsInVzZXJuYW1lIjoiYWRtaW4ifQ.dummy_token_for_testing"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_api_endpoints():
    """测试API端点"""
    print("开始测试API端点...")
    
    # 测试获取用户列表
    try:
        response = requests.get(f"{BASE_URL}/admin-users", headers=HEADERS, params={
            "skip": 0,
            "limit": 10
        })
        print(f"获取用户列表: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误信息: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试获取当前用户信息
    try:
        response = requests.get(f"{BASE_URL}/admin-users/current-user", headers=HEADERS)
        print(f"获取当前用户: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
        else:
            print(f"错误信息: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试获取用户统计信息
    try:
        response = requests.get(f"{BASE_URL}/admin-users/stats", headers=HEADERS)
        print(f"获取用户统计: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误信息: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试获取概览统计
    try:
        response = requests.get(f"{BASE_URL}/admin-users/stats/overview", headers=HEADERS)
        print(f"获取概览统计: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误信息: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_api_endpoints()