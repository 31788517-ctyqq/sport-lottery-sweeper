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
    print(f"响应头: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"登录成功!")
        print(f"Token: {data.get('access_token', 'N/A')[:50]}...")
        print(f"Token类型: {data.get('token_type', 'N/A')}")
        print(f"用户信息: {json.dumps(data.get('user', {}), indent=2, ensure_ascii=False)}")
    else:
        print(f"响应内容: {response.text}")
        
except Exception as e:
    print(f"异常: {e}")
    import traceback
    traceback.print_exc()