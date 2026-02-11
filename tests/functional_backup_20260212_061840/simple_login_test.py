import requests
url = "http://localhost:8000/api/v1/admin/login"
data = {"username": "admin", "password": "admin123"}
try:
    r = requests.post(url, json=data, timeout=5)
    print(f"状态码: {r.status_code}")
    if r.status_code == 200:
        print("[OK] 登录成功!")
        print(r.json())
    else:
        print(f"失败: {r.text}")
except Exception as e:
    print(f"错误: {e}")