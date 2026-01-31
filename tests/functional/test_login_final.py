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

print("测试登录API...")
print(f"URL: {url}")
print(f"用户名: admin")
print(f"密码: admin123")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"\n状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("[OK] 登录成功!")
        print(f"响应代码: {data.get('code')}")
        print(f"消息: {data.get('message')}")
        
        token_data = data.get('data', {})
        if token_data:
            print(f"访问令牌: {token_data.get('access_token', 'N/A')[:50]}...")
            print(f"令牌类型: {token_data.get('token_type', 'N/A')}")
            
            user_info = token_data.get('user', {})
            if user_info:
                print(f"用户ID: {user_info.get('id')}")
                print(f"用户名: {user_info.get('username')}")
                print(f"邮箱: {user_info.get('email')}")
                print(f"角色: {user_info.get('role', 'admin')}")
                print(f"是否超级用户: {user_info.get('is_superuser')}")
                print(f"创建时间: {user_info.get('created_at')}")
    else:
        print(f"[ERROR] 登录失败: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("[ERROR] 无法连接到后端服务，请确保后端正在运行")
except requests.exceptions.Timeout:
    print("[ERROR] 请求超时")
except Exception as e:
    print(f"[ERROR] 未知错误: {e}")