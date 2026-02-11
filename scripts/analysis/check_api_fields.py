import requests
import json

def check_api_fields():
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
        
        if response.status_code == 200:
            data = response.json()
            print(f"返回任务数量: {len(data)}")
            if data:
                print("第一个任务的所有字段:")
                first_task = data[0]
                for key, value in first_task.items():
                    print(f"  {key}: {value}")
                    
                print("\n关键字段检查:")
                print(f"  id: {first_task.get('id')}")
                print(f"  name: {first_task.get('name')}")
                print(f"  source_id: {first_task.get('source_id')}")
        else:
            print(f"请求失败: {response.text}")
            
    except Exception as e:
        print(f"请求错误: {e}")

if __name__ == "__main__":
    check_api_fields()