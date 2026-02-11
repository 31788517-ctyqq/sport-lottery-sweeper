import requests
import sys

url = "http://localhost:8000/api/v1/admin/login"
data = {"username": "admin", "password": "admin123"}

print("测试admin登录...")
try:
    r = requests.post(url, json=data, timeout=10)
    print(f"状态码: {r.status_code}")
    if r.status_code == 200:
        print("SUCCESS: 登录成功!")
        result = r.json()
        print(f"响应代码: {result.get('code')}")
        print(f"消息: {result.get('message')}")
        token_data = result.get('data', {})
        if token_data:
            print(f"访问令牌: {token_data.get('access_token', 'N/A')[:50]}...")
            user_info = token_data.get('user', {})
            print(f"用户ID: {user_info.get('id')}")
            print(f"用户名: {user_info.get('username')}")
            print(f"邮箱: {user_info.get('email')}")
            print(f"角色: {user_info.get('role', 'admin')}")
        sys.exit(0)
    else:
        print(f"FAILURE: 登录失败 - {r.text}")
        sys.exit(1)
except requests.exceptions.ConnectionError:
    print("ERROR: 无法连接到后端服务")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)