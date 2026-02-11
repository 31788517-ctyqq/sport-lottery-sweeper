"""
数据源管理模块端到端测试
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1/admin"

def test_data_source_module():
    print("开始数据源管理模块端到端测试...")
    print("=" * 60)
    
    # 1. 获取数据源列表
    print("1. 测试获取数据源列表...")
    try:
        response = requests.get(f"{BASE_URL}/sources", params={
            "page": 1,
            "size": 10
        })
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   ✓ 获取数据源列表成功，共 {data['data']['total']} 条记录")
                print(f"   ✓ 当前页面显示 {len(data['data']['items'])} 条记录")
            else:
                print("   ✗ 获取数据源列表失败")
        else:
            print(f"   ✗ 获取数据源列表失败，HTTP状态码: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 获取数据源列表异常: {e}")
    
    # 2. 获取单个数据源详情
    print("\n2. 测试获取单个数据源详情...")
    try:
        # 先获取一个存在的ID
        response = requests.get(f"{BASE_URL}/sources", params={"page": 1, "size": 1})
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data['data']['items']:
                source_id = data['data']['items'][0]['id']
                response = requests.get(f"{BASE_URL}/sources/{source_id}")
                if response.status_code == 200:
                    detail_data = response.json()
                    if detail_data.get("success"):
                        print(f"   ✓ 获取ID为 {source_id} 的数据源详情成功")
                    else:
                        print(f"   ✗ 获取ID为 {source_id} 的数据源详情失败")
                else:
                    print(f"   ✗ 获取数据源详情失败，HTTP状态码: {response.status_code}")
            else:
                print("   ! 无法获取数据源列表以进行详情测试")
        else:
            print(f"   ✗ 获取数据源列表以进行详情测试失败，HTTP状态码: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 获取数据源详情异常: {e}")
    
    # 3. 创建新数据源
    print("\n3. 测试创建新数据源...")
    try:
        new_source = {
            "name": f"测试数据源_{int(time.time())}",
            "type": "api",
            "url": "https://api.example.com/test",
            "config": {
                "api_key": "test_key",
                "timeout": 30
            },
            "status": "online"
        }
        response = requests.post(f"{BASE_URL}/sources", json=new_source)
        if response.status_code == 200:
            create_data = response.json()
            if create_data.get("success"):
                created_id = create_data['data']['id']
                print(f"   ✓ 创建数据源成功，ID: {created_id}")
                
                # 4. 更新刚创建的数据源
                print("\n4. 测试更新数据源...")
                try:
                    update_data = {
                        "name": f"更新后的测试数据源_{int(time.time())}",
                        "url": "https://api.example.com/updated",
                        "status": "offline"
                    }
                    response = requests.put(f"{BASE_URL}/sources/{created_id}", json=update_data)
                    if response.status_code == 200:
                        update_result = response.json()
                        if update_result.get("success"):
                            print(f"   ✓ 更新ID为 {created_id} 的数据源成功")
                            
                            # 5. 测试健康检查
                            print("\n5. 测试健康检查...")
                            try:
                                response = requests.get(f"{BASE_URL}/sources/{created_id}/health")
                                if response.status_code == 200:
                                    health_data = response.json()
                                    if health_data.get("success"):
                                        print(f"   ✓ 数据源健康检查成功")
                                    else:
                                        print(f"   ! 数据源健康检查返回失败状态，但请求成功")
                                else:
                                    print(f"   ! 数据源健康检查请求失败，HTTP状态码: {response.status_code}")
                            except Exception as e:
                                print(f"   ! 数据源健康检查异常: {e}")
                                
                        else:
                            print(f"   ✗ 更新数据源失败")
                    else:
                        print(f"   ✗ 更新数据源失败，HTTP状态码: {response.status_code}")
                except Exception as e:
                    print(f"   ✗ 更新数据源异常: {e}")
                    
                # 6. 删除刚创建的数据源
                print("\n6. 测试删除数据源...")
                try:
                    response = requests.delete(f"{BASE_URL}/sources/{created_id}")
                    if response.status_code == 200:
                        delete_data = response.json()
                        if delete_data.get("success"):
                            print(f"   ✓ 删除ID为 {created_id} 的数据源成功")
                        else:
                            print(f"   ✗ 删除数据源失败")
                    else:
                        print(f"   ✗ 删除数据源失败，HTTP状态码: {response.status_code}")
                except Exception as e:
                    print(f"   ✗ 删除数据源异常: {e}")
            else:
                print("   ✗ 创建数据源失败")
        else:
            print(f"   ✗ 创建数据源失败，HTTP状态码: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 创建数据源异常: {e}")
    
    # 7. 批量操作测试
    print("\n7. 测试批量操作...")
    try:
        # 获取前两个数据源ID进行批量操作测试
        response = requests.get(f"{BASE_URL}/sources", params={"page": 1, "size": 2})
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and len(data['data']['items']) >= 2:
                ids = [item['id'] for item in data['data']['items']]
                
                # 批量健康检查
                response = requests.post(f"{BASE_URL}/sources/batch/health", json={"ids": ids[:2]})
                if response.status_code == 200:
                    batch_health_data = response.json()
                    if batch_health_data.get("success"):
                        print(f"   ✓ 批量健康检查成功，检查了 {len(batch_health_data['data'])} 个数据源")
                    else:
                        print(f"   ! 批量健康检查返回失败状态")
                else:
                    print(f"   ! 批量健康检查请求失败，HTTP状态码: {response.status_code}")
                
                # 批量删除（不实际删除，仅测试接口）
                # 注意：这里不实际执行批量删除以免影响已有数据
                print("   - 批量删除接口可用性验证（跳过实际删除以保护数据）")
                
            else:
                print("   ! 数据不足，无法进行批量操作测试")
        else:
            print(f"   ! 获取数据源列表以进行批量操作测试失败")
    except Exception as e:
        print(f"   ! 批量操作测试异常: {e}")
    
    print("\n" + "=" * 60)
    print("数据源管理模块端到端测试完成!")

if __name__ == "__main__":
    test_data_source_module()