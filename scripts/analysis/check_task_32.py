import requests
import json

def check_task_list():
    try:
        # 获取任务列表
        response = requests.get('http://localhost:3000/api/admin/crawler/tasks?page=1&size=20')
        if response.status_code == 200:
            data = response.json()
            print("任务列表:")
            for task in data['data']['items']:
                print(f"ID: {task['id']}, Name: {task['name']}, Status: {task['status']}, Type: {task['task_type']}")
            
            # 检查是否存在ID为32的任务
            target_task = None
            for task in data['data']['items']:
                if task['id'] == 32:
                    target_task = task
                    break
            
            if target_task:
                print(f"\n找到ID为32的任务: {target_task}")
                return True
            else:
                print("\n没有找到ID为32的任务")
                print(f"可用的任务ID范围: {min(t['id'] for t in data['data']['items'])} - {max(t['id'] for t in data['data']['items'])}")
                return False
        else:
            print(f"获取任务列表失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"请求失败: {e}")
        return False

if __name__ == "__main__":
    check_task_list()