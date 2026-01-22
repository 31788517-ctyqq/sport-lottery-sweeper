import sys
sys.path.insert(0, 'backend')

import requests
import json

# 测试登录端点
url = "http://localhost:8000/api/v1/admin/login"
data = {
    "username": "admin",
    "password": "admin123"
}

print(f"发送POST请求到: {url}")
print(f"数据: {json.dumps(data, ensure_ascii=False)}")

try:
    response = requests.post(url, json=data, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应头:")
    for key, value in response.headers.items():
        if key.lower() in ['content-type', 'content-length']:
            print(f"  {key}: {value}")
    
    print(f"响应体: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ 登录成功!")
        print(f"代码: {result.get('code')}")
        print(f"消息: {result.get('message')}")
        data = result.get('data', {})
        if data:
            print(f"访问令牌: {data.get('access_token', 'N/A')}")
            user = data.get('user', {})
            print(f"用户信息:")
            for key, value in user.items():
                print(f"  {key}: {value}")
    else:
        print(f"\n❌ 登录失败: {response.text}")
        
except Exception as e:
    print(f"❌ 请求异常: {e}")
    import traceback
    traceback.print_exc()