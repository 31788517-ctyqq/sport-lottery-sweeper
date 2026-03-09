import requests
import json

def get_task_logs(task_id):
    try:
        # 获取任务日志
        response = requests.get(f'http://localhost:3000/api/admin/crawler/tasks/{task_id}/logs')
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"任务 {task_id} 的日志:")
            if 'data' in data and 'logs' in data['data']:
                for log in data['data']['logs']:
                    print(f"[{log.get('timestamp', 'N/A')}] [{log.get('level', 'INFO')}] {log.get('message', '')}")
            else:
                print("未找到日志数据")
        else:
            print(f"获取任务日志失败: {response.status_code}")
    except Exception as e:
        print(f"请求失败: {e}")

def get_task_details(task_id):
    try:
        # 获取任务详细信息
        response = requests.get(f'http://localhost:3000/api/admin/crawler/tasks/{task_id}')
        print(f"任务 {task_id} 的详细信息:")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"获取任务详情失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    task_id = 32
    print("获取任务详细信息:")
    get_task_details(task_id)
    print("\n获取任务日志:")
    get_task_logs(task_id)