import requests
import json

# 测试创建任务的POST请求，获取详细的错误信息
url = "http://localhost:8001/api/admin/crawler/tasks"

# 模拟前端发送的数据
payload = {
    "name": "测试任务",
    "source_id": 29,
    "task_type": "DATA_COLLECTION",
    "cron_expression": "0 * * * *",
    "is_active": True,
    "config": {}
}

headers = {
    "Content-Type": "application/json"
}

print("发送的请求数据:", json.dumps(payload, indent=2, ensure_ascii=False))

try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 422:
        print("\n422错误详情:")
        try:
            error_detail = response.json()
            print(json.dumps(error_detail, indent=2, ensure_ascii=False))
        except:
            print("无法解析错误详情")
            
        # 尝试获取FastAPI的验证错误详情
        if hasattr(response, 'headers'):
            print(f"\n响应头: {dict(response.headers)}")
except Exception as e:
    print(f"请求错误: {e}")