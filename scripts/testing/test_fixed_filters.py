import requests
import json
import time

def test_fixed_filters():
    print("等待服务重启完成...")
    time.sleep(5)  # 等待服务重启

    print("\n测试修复后的筛选功能...")
    
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
            print(f"   示例任务: ID={sample_task['id']}, 名称='{sample_task['name']}', "
                  f"类型='{sample_task['task_type']}', 状态='{sample_task['status']}'")
    else:
        print(f"   获取任务列表失败: {response.text}")
        return

    # 测试按大写状态筛选（前端通常使用大写）
    print("\n2. 测试按大写状态筛选 (STOPPED -> stopped):")
    response = requests.get(base_url, params={'page': 1, 'size': 20, 'status': 'STOPPED'})
    if response.status_code == 200:
        filtered_data = response.json()
        print(f"   按大写状态'STOPPED'筛选结果: {filtered_data['data']['total']} 个任务")
    else:
        print(f"   按大写状态筛选失败: {response.text}")

    # 测试按小写状态筛选
    print("\n3. 测试按小写状态筛选 (stopped):")
    response = requests.get(base_url, params={'page': 1, 'size': 20, 'status': 'stopped'})
    if response.status_code == 200:
        filtered_data = response.json()
        print(f"   按小写状态'stopped'筛选结果: {filtered_data['data']['total']} 个任务")
    else:
        print(f"   按小写状态筛选失败: {response.text}")

    # 测试按大写任务类型筛选
    print("\n4. 测试按大写任务类型筛选 (DATA_COLLECTION -> data_collection):")
    response = requests.get(base_url, params={'page': 1, 'size': 20, 'task_type': 'DATA_COLLECTION'})
    if response.status_code == 200:
        filtered_data = response.json()
        print(f"   按大写类型'DATA_COLLECTION'筛选结果: {filtered_data['data']['total']} 个任务")
    else:
        print(f"   按大写类型筛选失败: {response.text}")

    # 测试按小写任务类型筛选
    print("\n5. 测试按小写任务类型筛选 (data_collection):")
    response = requests.get(base_url, params={'page': 1, 'size': 20, 'task_type': 'DATA_COLLECTION'})
    if response.status_code == 200:
        filtered_data = response.json()
        print(f"   按小写类型'data_collection'筛选结果: {filtered_data['data']['total']} 个任务")
    else:
        print(f"   按小写类型筛选失败: {response.text}")

    # 测试组合筛选（大写状态 + 大写类型）
    print("\n6. 测试组合筛选 (大写类型 + 大写状态):")
    response = requests.get(base_url, params={
        'page': 1, 
        'size': 20, 
        'task_type': 'DATA_COLLECTION',
        'status': 'STOPPED'
    })
    if response.status_code == 200:
        filtered_data = response.json()
        print(f"   按大写类型'DATA_COLLECTION'和大写状态'STOPPED'组合筛选结果: {filtered_data['data']['total']} 个任务")
    else:
        print(f"   组合筛选失败: {response.text}")

    print("\n筛选功能测试完成!")

if __name__ == "__main__":
    test_fixed_filters()