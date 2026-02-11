import requests
import json
from datetime import datetime

# 创建一个新的任务来测试时间
url = "http://localhost:8001/api/admin/crawler/tasks"
payload = {
    "name": f"测试时间 {datetime.now().strftime('%H:%M:%S')}",
    "source_id": "DS008",  # 使用源ID
    "task_type": "DATA_COLLECTION",
    "cron_expression": "0 * * * *",
    "is_active": True,
    "config": {}
}

headers = {
    "Content-Type": "application/json"
}

print(f"当前时间: {datetime.now()}")
print(f"发送的请求: {json.dumps(payload, indent=2, ensure_ascii=False)}")

try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"响应状态: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        resp_data = response.json()
        created_at = resp_data['data']['created_at']
        print(f"API返回的创建时间: {created_at}")
except Exception as e:
    print(f"请求错误: {e}")