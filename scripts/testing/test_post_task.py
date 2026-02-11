import requests
import json

# 测试创建任务的POST请求
url = "http://localhost:8001/api/admin/crawler/tasks"

# 准备测试数据，使用存在的source_id
payload = {
    "name": "测试任务",
    "source_id": 29,  # 使用一个存在的source_id
    "task_type": "crawl",
    "cron_expression": "* * * * *",
    "is_active": True,
    "config": {}
}

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")