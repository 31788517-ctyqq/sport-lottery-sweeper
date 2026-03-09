import requests
import sys
import json

url = "http://localhost:8000/api/v1/admin/login"
data = {"username": "admin", "password": "admin123"}

print("测试登录...")
try:
    response = requests.post(url, json=data, timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"响应体: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n[OK] 登录成功!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0)
    else:
        print(f"\n[ERROR] 登录失败")
        sys.exit(1)
        
except Exception as e:
    print(f"[ERROR] 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)