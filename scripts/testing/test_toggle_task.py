import requests
import time

# 测试服务器地址
BASE_URL = "http://localhost:3000"

def create_test_task():
    """创建一个测试任务"""
    url = f"{BASE_URL}/api/admin/crawler/tasks"
    data = {
        "name": "Test Toggle Task",
        "source_id": "DS041",
        "task_type": "DATA_COLLECTION",
        "cron_expression": "* * * * *",
        "config": "{}"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"创建任务响应: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"任务创建成功，ID: {result['data']['id']}")
            return result['data']['id']
        else:
            print(f"创建任务失败: {response.text}")
            return None
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def trigger_task(task_id):
    """启动任务"""
    url = f"{BASE_URL}/api/admin/crawler/tasks/{task_id}/trigger"
    
    try:
        response = requests.post(url)
        print(f"启动任务响应: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"启动任务成功: {result['message']}")
            return True
        else:
            print(f"启动任务失败: {response.text}")
            return False
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def stop_task(task_id):
    """停止任务"""
    url = f"{BASE_URL}/api/admin/crawler/tasks/{task_id}/stop"
    
    try:
        response = requests.post(url)
        print(f"停止任务响应: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"停止任务成功: {result['message']}")
            return True
        else:
            print(f"停止任务失败: {response.text}")
            return False
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def get_task_details(task_id):
    """获取任务详情"""
    url = f"{BASE_URL}/api/admin/crawler/tasks/{task_id}"
    
    try:
        response = requests.get(url)
        print(f"获取任务详情响应: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            status = result['data']['status']
            print(f"当前任务状态: {status}")
            return status
        else:
            print(f"获取任务详情失败: {response.text}")
            return None
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def main():
    print("开始测试启动/停止功能...")
    
    # 创建测试任务
    task_id = create_test_task()
    if not task_id:
        print("无法创建测试任务，退出")
        return
    
    # 获取初始状态
    initial_status = get_task_details(task_id)
    
    # 启动任务
    print("\n--- 启动任务 ---")
    if trigger_task(task_id):
        time.sleep(2)  # 等待任务状态更新
        status_after_trigger = get_task_details(task_id)
        
        # 停止任务
        print("\n--- 停止任务 ---")
        if stop_task(task_id):
            time.sleep(2)  # 等待任务状态更新
            status_after_stop = get_task_details(task_id)
            
            print("\n--- 测试结果 ---")
            print(f"初始状态: {initial_status}")
            print(f"启动后状态: {status_after_trigger}")
            print(f"停止后状态: {status_after_stop}")
            
            if status_after_trigger == "RUNNING" and status_after_stop == "STOPPED":
                print("✅ 启动/停止功能测试通过!")
            else:
                print("❌ 启动/停止功能测试失败!")
        else:
            print("停止任务失败")
    else:
        print("启动任务失败")

if __name__ == "__main__":
    main()