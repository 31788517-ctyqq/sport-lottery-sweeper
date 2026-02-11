import requests
import json

def test_task_list_api():
    # 测试获取任务列表API
    url = "http://localhost:8001/api/admin/crawler/tasks"
    params = {
        "page": 1,
        "size": 20,
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
        
        if response.status_code == 200:
            data = response.json()
            print(f"返回任务数量: {len(data)}")
            if data:
                print("前3个任务信息:")
                for i, task in enumerate(data[:3]):
                    print(f"  {i+1}. ID: {task.get('id')}, 名称: {task.get('name')}, "
                          f"源ID: {task.get('source_id')}, 源源ID: {task.get('source_source_id')}")
            else:
                print("没有返回任何任务")
        else:
            print(f"请求失败: {response.text}")
            
    except Exception as e:
        print(f"请求错误: {e}")

if __name__ == "__main__":
    test_task_list_api()