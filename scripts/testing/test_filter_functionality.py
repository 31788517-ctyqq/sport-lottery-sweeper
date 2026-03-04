import requests
import json

def test_filters():
    print("测试任务控制台页面的筛选功能...")
    
    base_url = 'http://localhost:3000/api/admin/crawler/tasks'
    
    # 首先获取所有任务
    print("\n1. 获取所有任务:")
    response = requests.get(base_url, params={'page': 1, 'size': 20})
    if response.status_code == 200:
        data = response.json()
        total_tasks = data['data']['total']
        print(f"   总任务数: {total_tasks}")
        print(f"   返回任务数: {len(data['data']['items'])}")
        
        if len(data['data']['items']) > 0:
            sample_task = data['data']['items'][0]
            print(f"   示例任务: ID={sample_task['id']}, 名称='{sample_task['name']}', 类型='{sample_task['task_type']}', 状态='{sample_task['status']}'")
    else:
        print(f"   获取任务列表失败: {response.text}")
        return

    # 测试按名称筛选
    print("\n2. 测试按名称筛选:")
    if len(data['data']['items']) > 0:
        sample_name = data['data']['items'][0]['name']
        response = requests.get(base_url, params={'page': 1, 'size': 20, 'name': sample_name})
        if response.status_code == 200:
            filtered_data = response.json()
            print(f"   按名称'{sample_name}'筛选结果: {filtered_data['data']['total']} 个任务")
        else:
            print(f"   按名称筛选失败: {response.text}")

    # 测试按任务类型筛选
    print("\n3. 测试按任务类型筛选:")
    if len(data['data']['items']) > 0:
        sample_type = data['data']['items'][0]['task_type']
        response = requests.get(base_url, params={'page': 1, 'size': 20, 'task_type': sample_type})
        if response.status_code == 200:
            filtered_data = response.json()
            print(f"   按类型'{sample_type}'筛选结果: {filtered_data['data']['total']} 个任务")
        else:
            print(f"   按类型筛选失败: {response.text}")

    # 测试按状态筛选
    print("\n4. 测试按状态筛选:")
    if len(data['data']['items']) > 0:
        sample_status = data['data']['items'][0]['status']
        response = requests.get(base_url, params={'page': 1, 'size': 20, 'status': sample_status})
        if response.status_code == 200:
            filtered_data = response.json()
            print(f"   按状态'{sample_status}'筛选结果: {filtered_data['data']['total']} 个任务")
        else:
            print(f"   按状态筛选失败: {response.text}")

    # 测试按源ID筛选
    print("\n5. 测试按源ID筛选:")
    if len(data['data']['items']) > 0:
        sample_source_id = data['data']['items'][0]['source_id']
        response = requests.get(base_url, params={'page': 1, 'size': 20, 'source_id': sample_source_id})
        if response.status_code == 200:
            filtered_data = response.json()
            print(f"   按源ID'{sample_source_id}'筛选结果: {filtered_data['data']['total']} 个任务")
        else:
            print(f"   按源ID筛选失败: {response.text}")

    # 测试组合筛选
    print("\n6. 测试组合筛选:")
    if len(data['data']['items']) > 0:
        sample_type = data['data']['items'][0]['task_type']
        sample_status = data['data']['items'][0]['status']
        response = requests.get(base_url, params={
            'page': 1, 
            'size': 20, 
            'task_type': sample_type,
            'status': sample_status
        })
        if response.status_code == 200:
            filtered_data = response.json()
            print(f"   按类型'{sample_type}'和状态'{sample_status}'组合筛选结果: {filtered_data['data']['total']} 个任务")
        else:
            print(f"   组合筛选失败: {response.text}")

if __name__ == "__main__":
    test_filters()