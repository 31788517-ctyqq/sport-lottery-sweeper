import requests
import json

def test_get_task_logs():
    # 获取任务日志
    url = "http://localhost:8001/api/admin/crawler/tasks/16/logs"  # 使用新的任务ID
    
    print(f"发送GET请求到: {url}")

    try:
        response = requests.get(url)
        print(f"响应状态: {response.status_code}")
        print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"请求错误: {e}")

if __name__ == "__main__":
    test_get_task_logs()