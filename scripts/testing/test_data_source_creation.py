import requests
import json
from datetime import datetime

def test_create_data_source():
    # 测试创建数据源
    url = "http://localhost:8001/api/v1/admin/sources"
    
    # 使用时间戳确保名称唯一
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"测试数据源_{timestamp}"
    
    # 准备测试数据 - 只包含schema中定义的字段
    payload = {
        "name": name,
        "type": "api",  # 或者 "file"
        "status": "online",  # 状态可以是 online/offline/maintenance/error
        "url": "https://api.example.com/data",
        "config": {
            "timeout": 30,
            "max_retries": 3,
            "headers": {
                "User-Agent": "Mozilla/5.0 (compatible; TestBot/1.0)"
            }
        }
    }
    
    print("发送创建数据源请求...")
    print(f"请求URL: {url}")
    print(f"请求数据: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 数据源创建成功!")
                print(f"   ID: {result['data']['id']}")
                print(f"   源ID: {result['data']['source_id']}")
                print(f"   名称: {result['data']['name']}")
                
                # 验证是否出现在列表中
                print("\n验证数据源是否出现在列表中...")
                list_response = requests.get("http://localhost:8001/api/v1/admin/sources?page=1&size=20")
                if list_response.status_code == 200:
                    list_data = list_response.json()
                    if list_data.get("success"):
                        items = list_data['data']['items']
                        created_item = next((item for item in items if item['name'] == name), None)
                        if created_item:
                            print("✅ 数据源已成功显示在列表中!")
                            print(f"   列表中的ID: {created_item['id']}")
                            print(f"   列表中的源ID: {created_item['source_id']}")
                        else:
                            print("❌ 数据源未在列表中找到")
                    else:
                        print(f"❌ 获取列表失败: {list_data.get('message')}")
                else:
                    print(f"❌ 获取列表请求失败: {list_response.status_code}")
            else:
                print(f"❌ 数据源创建失败: {result.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求过程中发生错误: {e}")

if __name__ == "__main__":
    test_create_data_source()