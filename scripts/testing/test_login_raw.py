import requests
import json

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"

TEST_USER = {
    "username": "admin",
    "password": "admin123"
}

print("测试登录API...")
print(f"URL: {LOGIN_URL}")
print(f"用户: {TEST_USER}")

try:
    response = requests.post(
        LOGIN_URL,
        json=TEST_USER,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应文本: {response.text}")
    
    # 尝试解析JSON
    try:
        data = response.json()
        print(f"解析的JSON: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print("无法解析为JSON")
        
except Exception as e:
    print(f"异常: {e}")
    import traceback
    traceback.print_exc()