import requests
import json

def create_test_task():
    # 创建一个测试任务
    url = "http://localhost:8001/api/admin/crawler/tasks"
    payload = {
        "name": "测试任务",
        "task_type": "crawl",
        "source_id": "DS008",
        "cron_expression": "* * * * *",
        "is_active": True,
        "config": {"timeout": 30, "retry_count": 3}
    }

    headers = {
        "Content-Type": "application/json"
    }

    print(f"发送POST请求到: {url}")
    print(f"请求体: {json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print(f"响应状态: {response.status_code}")
        print(f"响应内容: {response.text}")
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"成功创建测试任务，ID: {result['data']['id']}")
                return result['data']['id']
            else:
                print("创建任务失败:", result.get("message"))
        else:
            print("请求失败")
    except Exception as e:
        print(f"请求错误: {e}")
        return None

if __name__ == "__main__":
    create_test_task()