import requests
import json

def test_delete_task():
    # 删除任务
    url = "http://localhost:8001/api/admin/crawler/tasks/1"
    
    print(f"发送DELETE请求到: {url}")

    try:
        response = requests.delete(url)
        print(f"响应状态: {response.status_code}")
        print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"请求错误: {e}")

if __name__ == "__main__":
    test_delete_task()