import requests
import json

# 测试创建任务的POST请求，获取详细的错误信息
url = "http://localhost:8001/api/admin/crawler/tasks"

# 使用更符合CrawlerTaskCreate模型的数据结构
payload = {
    "name": "测试任务",
    "source_id": 29,  # 使用一个存在的source_id
    "task_type": "crawl",
    "cron_expression": "* * * * *",
    "is_active": True,
    "config": {}  # 确保config是一个字典而不是字符串
}

headers = {
    "Content-Type": "application/json"
}

print("发送的请求数据:", json.dumps(payload, indent=2, ensure_ascii=False))

try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code >= 400:
        print("\n错误详情:")
        try:
            error_detail = response.json()
            print(json.dumps(error_detail, indent=2, ensure_ascii=False))
        except:
            print("无法解析错误详情")
except Exception as e:
    print(f"请求错误: {e}")