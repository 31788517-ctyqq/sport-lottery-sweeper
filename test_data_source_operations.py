import requests
import json
import time
import random

# 定义API端点
BASE_URL = "http://127.0.0.1:8000"

def test_data_source_operations():
    print("=== 开始测试数据源管理功能 ===\n")
    
    # 1. 首先获取现有数据源列表
    print("1. 获取现有数据源列表...")
    response = requests.get(f"{BASE_URL}/api/v1/admin/sources?page=1&size=20")
    if response.status_code == 200:
        data = response.json()
        sources = data.get('data', {}).get('items', [])
        print(f"   成功获取 {len(sources)} 个数据源\n")
    else:
        print(f"   获取数据源失败: {response.status_code}")
        return

    # 2. 测试编辑功能 - 选择第一个数据源进行更新
    if len(sources) > 0:
        source_to_update = sources[0]
        print(f"2. 测试编辑功能 - 更新数据源 '{source_to_update['name']}' (ID: {source_to_update['id']})")
        
        # 准备更新数据
        update_data = {
            "name": f"{source_to_update['name']} - 已编辑",
            "type": source_to_update.get("type", "api"),
            "url": source_to_update.get("url", ""),
            "config": source_to_update.get("config", {}),
            "status": source_to_update.get("status", True)
        }
        
        response = requests.put(f"{BASE_URL}/api/v1/admin/sources/{source_to_update['id']}", 
                                json=update_data)
        if response.status_code == 200:
            updated_source = response.json()
            print(f"   编辑成功! 更新后的名称: '{updated_source['data']['name']}'\n")
        else:
            print(f"   编辑失败: {response.status_code}, 错误: {response.text}\n")

    # 3. 测试删除功能 - 创建一个新的数据源然后删除它
    print("3. 测试删除功能...")
    
    # 创建一个临时数据源用于测试删除
    test_source_data = {
        "name": f"测试删除数据源-{int(time.time())}",
        "type": "api",
        "url": "https://api.example.com/test-delete",
        "config": {
            "method": "GET",
            "timeout": 30,
            "headers": {"User-Agent": "TestBot/1.0"}
        },
        "status": True
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/admin/sources", json=test_source_data)
    if response.status_code == 200:
        created_source = response.json()['data']
        print(f"   创建测试数据源成功 (ID: {created_source['id']})")
        
        # 删除刚创建的数据源
        response = requests.delete(f"{BASE_URL}/api/v1/admin/sources/{created_source['id']}")
        if response.status_code == 200:
            print(f"   删除测试数据源成功 (ID: {created_source['id']})\n")
        else:
            print(f"   删除测试数据源失败: {response.status_code}, 错误: {response.text}\n")
    else:
        print(f"   创建测试数据源失败: {response.status_code}, 错误: {response.text}\n")

    # 4. 测试批量删除功能 - 创建多个数据源然后批量删除
    print("4. 测试批量删除功能...")
    
    # 创建两个临时数据源用于测试批量删除
    test_sources_to_delete = []
    for i in range(2):
        test_source_data = {
            "name": f"批量删除测试数据源-{int(time.time())}-{i}",
            "type": "api",
            "url": f"https://api.example{i}.com/test",
            "config": {
                "method": "GET",
                "timeout": 30,
                "headers": {"User-Agent": "TestBot/1.0"}
            },
            "status": True
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/admin/sources", json=test_source_data)
        if response.status_code == 200:
            created_source = response.json()['data']
            test_sources_to_delete.append(created_source['id'])
            print(f"   创建批量删除测试数据源成功 (ID: {created_source['id']})")
        else:
            print(f"   创建批量删除测试数据源失败: {response.status_code}, 错误: {response.text}")

    if len(test_sources_to_delete) > 0:
        # 批量删除刚创建的数据源
        batch_delete_data = {"ids": test_sources_to_delete}
        response = requests.delete(f"{BASE_URL}/api/v1/admin/sources/batch", json=batch_delete_data)
        if response.status_code == 200:
            print(f"   批量删除 {len(test_sources_to_delete)} 个数据源成功\n")
        else:
            print(f"   批量删除失败: {response.status_code}, 错误: {response.text}\n")
    
    # 5. 测试批量健康检查功能
    print("5. 测试批量健康检查功能...")
    
    # 获取一些数据源进行健康检查
    response = requests.get(f"{BASE_URL}/api/v1/admin/sources?page=1&size=3")
    if response.status_code == 200:
        data = response.json()
        sources_for_health_check = data.get('data', {}).get('items', [])[:2]  # 取前两个
        
        if len(sources_for_health_check) > 0:
            ids = [source['id'] for source in sources_for_health_check]
            health_check_data = {"ids": ids}
            
            response = requests.post(f"{BASE_URL}/api/v1/admin/sources/batch/health", json=health_check_data)
            if response.status_code == 200:
                print(f"   批量健康检查 {len(ids)} 个数据源成功")
                result = response.json()
                print(f"   结果: {result.get('message', 'N/A')}\n")
            else:
                print(f"   批量健康检查失败: {response.status_code}, 错误: {response.text}\n")
        else:
            print("   没有足够的数据源用于健康检查测试\n")
    else:
        print(f"   获取数据源用于健康检查测试失败: {response.status_code}\n")
    
    print("=== 测试完成 ===")

if __name__ == "__main__":
    test_data_source_operations()