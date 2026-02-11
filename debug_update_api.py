"""
调试数据源更新API
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1/admin"

def debug_update_api():
    print("调试数据源更新API...")
    
    # 创建一个新的数据源用于测试
    new_source = {
        "name": f"调试测试数据源_{int(time.time())}",
        "type": "api",
        "url": "https://api.example.com/test",
        "config": {
            "api_key": "test_key",
            "timeout": 30
        },
        "status": "online"
    }
    
    print("1. 创建新数据源...")
    response = requests.post(f"{BASE_URL}/sources", json=new_source)
    print(f"   创建响应: {response.status_code}")
    print(f"   响应内容: {response.text}")
    
    if response.status_code == 200:
        create_data = response.json()
        if create_data.get("success"):
            source_id = create_data['data']['id']
            print(f"   成功创建数据源，ID: {source_id}")
            
            # 尝试更新
            print(f"\n2. 尝试更新ID为 {source_id} 的数据源...")
            update_data = {
                "name": f"更新后的测试数据源_{int(time.time())}",
                "url": "https://api.example.com/updated",
                "status": "offline"
            }
            
            response = requests.put(f"{BASE_URL}/sources/{source_id}", json=update_data)
            print(f"   更新响应: {response.status_code}")
            print(f"   响应内容: {response.text}")
            
            # 清理：删除测试数据源
            print(f"\n3. 清理 - 删除ID为 {source_id} 的数据源...")
            delete_response = requests.delete(f"{BASE_URL}/sources/{source_id}")
            print(f"   删除响应: {delete_response.status_code}")
            print(f"   删除响应内容: {delete_response.text}")
        else:
            print("   创建失败")
    else:
        print("   创建请求失败")

if __name__ == "__main__":
    debug_update_api()