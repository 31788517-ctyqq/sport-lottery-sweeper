import requests
try:
    response = requests.get("http://localhost:8000/", timeout=5)
    print(f"后端响应状态: {response.status_code}")
    print(f"响应文本: {response.text[:200]}")
except requests.exceptions.ConnectionError:
    print("后端未运行或无法连接")
except Exception as e:
    print(f"错误: {e}")