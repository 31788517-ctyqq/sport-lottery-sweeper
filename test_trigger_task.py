import requests
import json
from datetime import datetime

def test_trigger_task():
    # 先获取任务列表，选择其中一个任务进行测试
    print("获取任务列表...")
    try:
        response = requests.get("http://localhost:8001/api/v1/admin/tasks")
        if response.status_code == 200:
            tasks_data = response.json()
            print(f"任务列表响应: {json.dumps(tasks_data, indent=2, ensure_ascii=False)}")
            
            if tasks_data.get("success") and tasks_data.get("data", {}).get("items"):
                # 获取第一个任务ID进行测试
                first_task = tasks_data["data"]["items"][0]
                task_id = first_task["id"]
                print(f"选择任务ID: {task_id} 进行测试")
                
                # 测试触发任务 - 尝试多个可能的API路径
                api_paths = [
                    f"http://localhost:8001/api/v1/admin/tasks/{task_id}/trigger",
                    f"http://localhost:8001/api/v1/crawler/tasks/{task_id}/trigger",
                    f"http://localhost:8001/api/admin/crawler/tasks/{task_id}/trigger"
                ]
                
                for path in api_paths:
                    print(f"\n正在尝试触发任务API路径: {path}")
                    trigger_response = requests.post(path)
                    
                    print(f"触发任务响应状态码: {trigger_response.status_code}")
                    if trigger_response.status_code == 200:
                        result = trigger_response.json()
                        print(f"触发任务响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
                        
                        if result.get("success") or "status" in result:
                            print(f"✅ 任务 {task_id} 触发成功!")
                            print(f"   消息: {result.get('message', 'N/A')}")
                            print(f"   状态: {result.get('status', 'N/A')}")
                            return  # 成功则退出
                        else:
                            print(f"❌ 任务 {task_id} 触发失败!")
                            print(f"   错误: {result.get('message', 'Unknown error')}")
                    else:
                        print(f"❌ API路径 {path} 返回状态码: {trigger_response.status_code}")
                        print(f"   响应内容: {trigger_response.text}")
            else:
                print("❌ 没有找到任务，请先创建一个任务")
        else:
            print(f"❌ 获取任务列表失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    test_trigger_task()