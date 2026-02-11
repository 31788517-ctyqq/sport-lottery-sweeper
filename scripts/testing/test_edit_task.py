import requests
import json

def test_edit_task():
    # 更新任务
    url = "http://localhost:8001/api/admin/crawler/tasks/1"
    payload = {
        "name": "更新后的任务名称",
        "task_type": "crawl",
        "source_id": "DS008",  # 使用业务源ID
        "cron_expression": "0 */2 * * *",
        "is_active": True,
        "config": {"timeout": 60, "retry_count": 3}
    }

    headers = {
        "Content-Type": "application/json"
    }

    print(f"发送PUT请求到: {url}")
    print(f"请求体: {json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        response = requests.put(url, headers=headers, data=json.dumps(payload))
        print(f"响应状态: {response.status_code}")
        print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"请求错误: {e}")

if __name__ == "__main__":
    test_edit_task()