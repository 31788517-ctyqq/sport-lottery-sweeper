import requests
import json

# 模拟前端现在会发送的数据格式
url = "http://localhost:8001/api/admin/crawler/tasks"

# 模拟前端修改后的数据结构
payload = {
    "name": "测试任务",
    "source_id": 29,  # 现在是数字类型
    "task_type": "DATA_COLLECTION",  # 从前端选项中选取的值
    "cron_expression": "0 * * * *",  # 新增的必需字段
    "is_active": True,  # 默认值
    "config": {}  # 解析后的JSON对象
}

headers = {
    "Content-Type": "application/json"
}

print("模拟前端发送的请求数据:", json.dumps(payload, indent=2, ensure_ascii=False))

try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"\n状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 200:
        print("\n✓ 任务创建成功！前端现在应该能够正常创建任务。")
    else:
        print(f"\n✗ 仍有错误，状态码: {response.status_code}")
        try:
            error_detail = response.json()
            print("错误详情:", json.dumps(error_detail, indent=2, ensure_ascii=False))
        except:
            print("无法解析错误详情")
            
except Exception as e:
    print(f"请求错误: {e}")