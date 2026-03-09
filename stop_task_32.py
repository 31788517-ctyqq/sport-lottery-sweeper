import requests

def stop_task_32():
    # 停止任务
    stop_url = f"http://localhost:3000/api/admin/crawler/tasks/32/stop"
    
    try:
        print("尝试停止任务ID 32...")
        stop_response = requests.post(stop_url)
        print(f"停止任务响应状态: {stop_response.status_code}")
        
        if stop_response.status_code == 200:
            result = stop_response.json()
            print(f"停止任务结果: {result}")
        else:
            print(f"停止任务失败: {stop_response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    stop_task_32()