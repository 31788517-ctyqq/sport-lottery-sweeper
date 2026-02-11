import requests

def get_all_tasks():
    # 获取所有任务
    tasks_url = "http://localhost:3000/api/admin/crawler/tasks?page=1&size=100"
    
    print("获取所有任务列表...")
    print("="*60)
    
    try:
        response = requests.get(tasks_url)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            tasks = data.get('data', [])
            
            if isinstance(tasks, list) and len(tasks) > 0:
                print(f"找到 {len(tasks)} 个任务:")
                for task in tasks:
                    print(f"  - ID: {task.get('id')}, 名称: {task.get('name')}, 状态: {task.get('status')}")
            elif isinstance(tasks, dict) and 'items' in tasks:
                # 分页格式
                items = tasks.get('items', [])
                print(f"找到 {len(items)} 个任务:")
                for task in items:
                    print(f"  - ID: {task.get('id')}, 名称: {task.get('name')}, 状态: {task.get('status')}")
            else:
                print("未找到任何任务")
        else:
            print(f"获取任务列表失败: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    get_all_tasks()