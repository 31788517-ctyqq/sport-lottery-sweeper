import requests
import time

def test_updated_task_execution():
    task_id = 32
    
    print("测试更新配置后的任务执行...")
    print("="*60)
    
    # 1. 启动任务
    print("1. 正在启动任务...")
    trigger_url = f"http://localhost:3000/api/admin/crawler/tasks/{task_id}/trigger"
    
    try:
        trigger_response = requests.post(trigger_url)
        if trigger_response.status_code == 200:
            trigger_result = trigger_response.json()
            print(f"   ✅ 任务启动成功: {trigger_result['message']}")
            print(f"   任务状态: {trigger_result['data']['status']}")
        else:
            print(f"   ❌ 任务启动失败: {trigger_response.status_code} - {trigger_response.text}")
            return
    except Exception as e:
        print(f"   ❌ 任务启动异常: {e}")
        return
    
    # 2. 等待几秒钟，让任务执行
    print("2. 等待任务执行...")
    time.sleep(5)
    
    # 3. 检查任务状态
    print("3. 检查任务状态...")
    task_url = f"http://localhost:3000/api/admin/crawler/tasks/{task_id}"
    
    try:
        task_response = requests.get(task_url)
        if task_response.status_code == 200:
            task_data = task_response.json()['data']
            print(f"   任务状态: {task_data['status']}")
            print(f"   上次运行时间: {task_data['last_run_time']}")
        else:
            print(f"   ❌ 获取任务状态失败: {task_response.status_code}")
    except Exception as e:
        print(f"   ❌ 获取任务状态异常: {e}")
    
    # 4. 检查最新日志
    print("4. 检查最新日志...")
    logs_url = f"http://localhost:3000/api/admin/crawler/tasks/{task_id}/logs"
    
    try:
        logs_response = requests.get(logs_url)
        if logs_response.status_code == 200:
            logs_data = logs_response.json()['data']
            if logs_data['items']:
                latest_log = logs_data['items'][0]
                print(f"   最新日志状态: {latest_log['status']}")
                print(f"   消息: {latest_log['message']}")
                print(f"   处理记录数: {latest_log['records_processed']}")
                print(f"   成功记录数: {latest_log['records_success']}")
                print(f"   失败记录数: {latest_log['records_failed']}")
                
                # 检查是否处理了数据
                if latest_log['records_processed'] > 0:
                    print("   🎉 任务成功处理了数据！")
                else:
                    print("   ⚠️  任务仍未处理任何数据，可能仍有问题")
            else:
                print("   ❌ 没有找到日志记录")
        else:
            print(f"   ❌ 获取日志失败: {logs_response.status_code}")
    except Exception as e:
        print(f"   ❌ 获取日志异常: {e}")
    
    # 5. 停止任务
    print("5. 正在停止任务...")
    stop_url = f"http://localhost:3000/api/admin/crawler/tasks/{task_id}/stop"
    
    try:
        stop_response = requests.post(stop_url)
        if stop_response.status_code == 200:
            stop_result = stop_response.json()
            print(f"   ✅ 任务停止成功: {stop_result['message']}")
            print(f"   最终状态: {stop_result['data']['status']}")
        else:
            print(f"   ❌ 任务停止失败: {stop_response.status_code} - {stop_response.text}")
    except Exception as e:
        print(f"   ❌ 任务停止异常: {e}")
    
    print("="*60)

if __name__ == "__main__":
    test_updated_task_execution()