import requests
import json

def test_detailed_error():
    # 测试获取任务列表API
    url = "http://localhost:8001/api/admin/crawler/tasks"
    params = {
        "page": 1,
        "size": 3,
        "name": "",
        "task_type": "",
        "status": "",
        "source_id": ""
    }

    print(f"发送请求到: {url}")
    print(f"参数: {params}")

    try:
        response = requests.get(url, params=params)
        print(f"响应状态: {response.status_code}")
        print(f"响应内容: {response.text}")
        
    except Exception as e:
        print(f"请求错误: {e}")

if __name__ == "__main__":
    test_detailed_error()