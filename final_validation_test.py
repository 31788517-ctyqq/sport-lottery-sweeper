import requests
import time

# 测试服务器地址
BASE_URL = "http://localhost:3000"

def create_test_task():
    """创建一个测试任务"""
    url = f"{BASE_URL}/api/admin/crawler/tasks"
    data = {
        "name": "Final Validation Test Task",
        "source_id": "DS042",
        "task_type": "DATA_COLLECTION",
        "cron_expression": "* * * * *",
        "config": "{}"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"创建任务响应: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 任务创建成功，ID: {result['data']['id']}")
            return result['data']['id']
        else:
            print(f"❌ 创建任务失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def trigger_task(task_id):
    """启动任务"""
    url = f"{BASE_URL}/api/admin/crawler/tasks/{task_id}/trigger"
    
    try:
        response = requests.post(url)
        print(f"启动任务响应: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 启动任务成功: {result['message']}")
            return True
        else:
            print(f"❌ 启动任务失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def stop_task(task_id):
    """停止任务"""
    url = f"{BASE_URL}/api/admin/crawler/tasks/{task_id}/stop"
    
    try:
        response = requests.post(url)
        print(f"停止任务响应: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 停止任务成功: {result['message']}")
            return True
        else:
            print(f"❌ 停止任务失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
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
            print(f"❌ 获取任务详情失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def get_task_logs(task_id):
    """获取任务日志"""
    url = f"{BASE_URL}/api/admin/crawler/tasks/{task_id}/logs"
    
    try:
        response = requests.get(url)
        print(f"获取任务日志响应: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            logs = result['data']['items']  # 修复：获取items数组
            print(f"✅ 获取到 {len(logs)} 条日志记录")
            if logs:
                print("最近几条日志:")
                for log in logs[-3:]:  # 显示最后3条日志
                    print(f"  - {log['status']} | {log.get('message', 'No message')} | {log.get('created_at', 'No time')}")
            return logs
        else:
            print(f"❌ 获取任务日志失败: {response.text}")
            return []
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return []

def main():
    print("="*60)
    print("竞彩足球扫盘系统 - 启动/停止功能完整验证")
    print("="*60)
    
    # 创建测试任务
    print("\n📋 步骤1: 创建测试任务")
    task_id = create_test_task()
    if not task_id:
        print("❌ 无法创建测试任务，退出")
        return
    
    # 获取初始状态
    print(f"\n🔍 步骤2: 获取任务初始状态 (ID: {task_id})")
    initial_status = get_task_details(task_id)
    
    # 启动任务
    print(f"\n🚀 步骤3: 启动任务")
    if trigger_task(task_id):
        time.sleep(2)  # 等待任务状态更新
        status_after_trigger = get_task_details(task_id)
        
        # 获取启动后的日志
        print(f"\n📝 步骤4: 获取启动后日志")
        logs_after_trigger = get_task_logs(task_id)
        
        # 停止任务
        print(f"\n⏹️  步骤5: 停止任务")
        if stop_task(task_id):
            time.sleep(2)  # 等待任务状态更新
            status_after_stop = get_task_details(task_id)
            
            # 获取停止后的日志
            print(f"\n📋 步骤6: 获取停止后日志")
            logs_after_stop = get_task_logs(task_id)
            
            print("\n" + "="*60)
            print("📊 测试结果汇总")
            print("="*60)
            print(f"初始状态: {initial_status}")
            print(f"启动后状态: {status_after_trigger}")
            print(f"停止后状态: {status_after_stop}")
            print(f"启动后日志数: {len(logs_after_trigger)}")
            print(f"停止后日志数: {len(logs_after_stop)}")
            
            # 验证结果
            success_checks = []
            
            if status_after_trigger == "RUNNING":
                success_checks.append("✅ 任务成功启动")
            else:
                success_checks.append("❌ 任务未能正确启动")
                
            if status_after_stop == "STOPPED":
                success_checks.append("✅ 任务成功停止")
            else:
                success_checks.append("❌ 任务未能正确停止")
                
            if len(logs_after_trigger) > 0:
                success_checks.append("✅ 启动后有日志记录")
            else:
                success_checks.append("❌ 启动后无日志记录")
                
            if len(logs_after_stop) > len(logs_after_trigger):
                success_checks.append("✅ 停止后增加了日志记录")
            else:
                success_checks.append("⚠️  停止后未增加日志记录")
            
            print("\n📋 详细验证结果:")
            for check in success_checks:
                print(f"  {check}")
            
            overall_success = all([
                status_after_trigger == "RUNNING",
                status_after_stop == "STOPPED",
                len(logs_after_trigger) > 0
            ])
            
            print(f"\n🎯 整体测试结果: {'✅ 通过' if overall_success else '❌ 未通过'}")
            print("="*60)
        else:
            print("❌ 停止任务失败")
    else:
        print("❌ 启动任务失败")

if __name__ == "__main__":
    main()