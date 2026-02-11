import requests
import json

# 测试批量删除API
url = 'http://localhost:3000/api/admin/crawler/tasks/batch-delete'
headers = {'Content-Type': 'application/json'}

# 首先获取一些任务
response = requests.get('http://localhost:3000/api/admin/crawler/tasks?page=1&size=5')
if response.status_code == 200:
    data = response.json()
    print(f"获取任务列表成功，共{data['data']['total']}个任务")
    
    # 获取前几个任务ID进行测试
    items = data['data']['items']
    if len(items) > 0:
        test_ids = [item['id'] for item in items[:2]]  # 取前两个任务ID
        print(f"使用任务ID进行批量删除测试: {test_ids}")
        
        # 测试批量删除API
        payload = {'ids': test_ids}
        print(f"发送请求数据: {payload}")
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print(f"批量删除 - Status Code: {response.status_code}")
        print(f"批量删除 - Response: {response.text}")
    else:
        print("没有找到任何任务进行删除测试")
else:
    print(f"获取任务列表失败: {response.text}")


def test_batch_delete_tasks():
    # 创建几个测试任务
    url_create = "http://localhost:8001/api/admin/crawler/tasks"
    payloads = [
        {
            "name": "批量删除测试任务1",
            "task_type": "crawl",
            "source_id": "DS008",
            "cron_expression": "* * * * *",
            "is_active": True,
            "config": {"timeout": 30, "retry_count": 3}
        },
        {
            "name": "批量删除测试任务2",
            "task_type": "crawl",
            "source_id": "DS008",
            "cron_expression": "* * * * *",
            "is_active": True,
            "config": {"timeout": 30, "retry_count": 3}
        },
        {
            "name": "批量删除测试任务3",
            "task_type": "crawl",
            "source_id": "DS008",
            "cron_expression": "* * * * *",
            "is_active": True,
            "config": {"timeout": 30, "retry_count": 3}
        }
    ]
    
    created_task_ids = []
    
    print("创建测试任务...")
    for payload in payloads:
        try:
            response = requests.post(url_create, json=payload)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    created_task_ids.append(result['data']['id'])
                    print(f"成功创建任务，ID: {result['data']['id']}")
                else:
                    print(f"创建任务失败: {result.get('message')}")
            else:
                print(f"创建任务请求失败，状态码: {response.status_code}")
        except Exception as e:
            print(f"创建任务时发生错误: {e}")
    
    if len(created_task_ids) >= 2:
        print(f"\n将要批量删除任务 IDs: {created_task_ids[:2]}")
        
        # 测试批量删除
        url_batch_delete = "http://localhost:8001/api/admin/crawler/tasks/batch"
        delete_payload = {"ids": created_task_ids[:2]}
        
        print(f"发送批量删除请求到: {url_batch_delete}")
        print(f"请求体: {json.dumps(delete_payload, indent=2, ensure_ascii=False)}")
        
        try:
            response = requests.delete(url_batch_delete, json=delete_payload)
            print(f"响应状态: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"批量删除成功: {result.get('message')}")
                else:
                    print(f"批量删除失败: {result.get('message')}")
            else:
                print("批量删除请求失败")
        except Exception as e:
            print(f"批量删除时发生错误: {e}")
    else:
        print("未能创建足够的测试任务进行批量删除测试")

if __name__ == "__main__":
    test_batch_delete_tasks()