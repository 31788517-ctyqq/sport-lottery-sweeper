import requests
import time

def monitor_task():
    task_url = "http://localhost:3000/api/admin/crawler/tasks/32"
    logs_url = "http://localhost:3000/api/admin/crawler/tasks/32/logs"
    
    print("开始监控任务ID 32的执行情况...")
    print("="*60)
    
    # 初始状态
    try:
        task_response = requests.get(task_url)
        if task_response.status_code == 200:
            task_data = task_response.json()['data']
            print(f"初始状态: {task_data['status']}")
            print(f"上次运行时间: {task_data['last_run_time']}")
            print(f"运行次数: {task_data['run_count']}")
            print(f"成功次数: {task_data['success_count']}")
            print(f"错误次数: {task_data['error_count']}")
        else:
            print(f"获取任务详情失败: {task_response.status_code}")
            return
    except Exception as e:
        print(f"请求失败: {e}")
        return

    # 持续监控
    for i in range(10):  # 监控10次
        time.sleep(5)  # 等待5秒
        print("-" * 60)
        print(f"第 {i+1} 次检查 ({time.strftime('%H:%M:%S')})")
        
        try:
            # 获取任务状态
            task_response = requests.get(task_url)
            if task_response.status_code == 200:
                task_data = task_response.json()['data']
                print(f"状态: {task_data['status']}")
                print(f"上次运行时间: {task_data['last_run_time']}")
                print(f"运行次数: {task_data['run_count']}")
                print(f"成功次数: {task_data['success_count']}")
                print(f"错误次数: {task_data['error_count']}")
            else:
                print(f"获取任务详情失败: {task_response.status_code}")
            
            # 获取日志
            logs_response = requests.get(logs_url)
            if logs_response.status_code == 200:
                logs_data = logs_response.json()['data']
                print(f"日志总数: {logs_data['total']}")
                if logs_data['items']:
                    latest_log = logs_data['items'][-1]  # 最新的日志
                    print(f"最新日志: {latest_log['message']}")
                    print(f"日志时间: {latest_log['created_at']}")
            else:
                print(f"获取日志失败: {logs_response.status_code}")
                
        except Exception as e:
            print(f"请求失败: {e}")
    
    print("="*60)
    print("监控结束")

if __name__ == "__main__":
    monitor_task()