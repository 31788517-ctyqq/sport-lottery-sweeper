import requests
import json

def debug_batch_delete():
    print("开始调试批量删除API...")
    
    # 首先获取一些任务
    print("\n1. 获取任务列表...")
    response = requests.get('http://localhost:3000/api/admin/crawler/tasks?page=1&size=5')
    if response.status_code == 200:
        data = response.json()
        print(f"   任务列表获取成功，共{data['data']['total']}个任务")
        
        # 获取前几个任务ID进行测试
        items = data['data']['items']
        if len(items) > 0:
            test_ids = [item['id'] for item in items[:2]]  # 取前两个任务ID
            print(f"   选择任务ID进行批量删除测试: {test_ids}")
            
            # 测试批量删除API
            print("\n2. 测试批量删除API...")
            url = 'http://localhost:3000/api/admin/crawler/tasks/batch-delete'
            headers = {'Content-Type': 'application/json'}
            payload = {'ids': test_ids}
            
            print(f"   发送请求到: {url}")
            print(f"   请求头: {headers}")
            print(f"   请求体: {json.dumps(payload)}")
            
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            print(f"   响应状态码: {response.status_code}")
            print(f"   响应内容: {response.text}")
            
            if response.status_code == 200:
                print("   ✓ 批量删除成功!")
            else:
                print(f"   × 批量删除失败，状态码: {response.status_code}")
                
                # 检查是否是task_ids问题
                if "task_ids不能为空" in response.text:
                    print("   提示: 服务可能没有重启，仍使用旧的代码")
        else:
            print("   没有找到任何任务进行删除测试")
    else:
        print(f"   获取任务列表失败: {response.text}")

def check_api_endpoints():
    print("\n3. 检查API端点是否存在...")
    endpoints = [
        'http://localhost:3000/api/admin/crawler/tasks',
        'http://localhost:3000/api/admin/crawler/tasks/batch-delete',
        'http://localhost:3000/api/admin/crawler/tasks/statistics'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.head(endpoint)
            print(f"   {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   {endpoint}: 连接失败 - {e}")

if __name__ == "__main__":
    debug_batch_delete()
    check_api_endpoints()