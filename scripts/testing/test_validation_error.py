import requests
import json

# 测试API - 发送无效数据以触发验证错误
url = "http://localhost:8000/api/v1/data-source-100qiu/"

# 构造无效请求数据（缺少必要字段）
data = {}

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")