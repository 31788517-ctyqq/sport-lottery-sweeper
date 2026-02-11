import requests
import json
from datetime import datetime

def test_create_task():
    # 创建任务
    url = "http://localhost:8001/api/admin/crawler/tasks"
    payload = {
        "name": f"最终测试_{datetime.now().strftime('%H%M%S')}",
        "source_id": "DS008",  # 使用DS008源ID
        "task_type": "crawl",
        "cron_expression": "0 */3 * * *",  # 每3小时执行一次
        "is_active": True,
        "config": {"timeout": 60, "retry_count": 2}
    }

    headers = {
        "Content-Type": "application/json"
    }

    print(f"创建任务请求: {json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print(f"响应状态: {response.status_code}")
        
        if response.status_code == 200:
            resp_data = response.json()
            print(f"API返回的创建时间: {resp_data['data']['created_at']}")
            print(f"任务ID: {resp_data['data']['id']}")
            print(f"源ID: {resp_data['data']['source_id']}")  # 这现在是DS008格式
        else:
            print(f"创建任务失败: {response.text}")
            
    except Exception as e:
        print(f"请求错误: {e}")

if __name__ == "__main__":
    test_create_task()