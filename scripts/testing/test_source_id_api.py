import requests
import json

# 首先获取一个存在的数据源的source_id
print("获取数据源列表...")
url = "http://localhost:8001/api/v1/admin/sources?page=1&size=10"
try:
    response = requests.get(url)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data['success'] and len(data['data']['items']) > 0:
            first_source = data['data']['items'][0]
            source_id = first_source['source_id']
            print(f"获取到的第一个数据源的source_id: {source_id}")
            
            # 使用这个source_id创建任务
            print(f"\n使用source_id {source_id} 创建任务...")
            task_url = "http://localhost:8001/api/admin/crawler/tasks"
            task_payload = {
                "name": "测试任务",
                "source_id": source_id,  # 使用实际的source_id
                "task_type": "DATA_COLLECTION",
                "cron_expression": "0 * * * *",
                "is_active": True,
                "config": {}
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            print(f"发送的请求数据: {json.dumps(task_payload, indent=2, ensure_ascii=False)}")
            
            task_response = requests.post(task_url, headers=headers, data=json.dumps(task_payload))
            print(f"任务创建状态码: {task_response.status_code}")
            print(f"任务创建响应: {task_response.text}")
        else:
            print("没有找到任何数据源")
    else:
        print(f"获取数据源失败: {response.text}")
except Exception as e:
    print(f"请求错误: {e}")