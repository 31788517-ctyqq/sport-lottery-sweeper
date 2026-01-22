import requests
import json

url = "http://localhost:8000/api/v1/admin/login"

payload = {
    "username": "admin",
    "password": "admin123"
}

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应头: {response.headers}")
    print(f"响应体: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ 登录成功!")
        print(f"访问令牌: {data.get('access_token', 'N/A')}")
        print(f"用户信息: {json.dumps(data.get('user', {}), indent=2, ensure_ascii=False)}")
    else:
        print(f"\n❌ 登录失败: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ 无法连接到后端服务，请确保后端正在运行")
except requests.exceptions.Timeout:
    print("❌ 请求超时")
except Exception as e:
    print(f"❌ 未知错误: {e}")