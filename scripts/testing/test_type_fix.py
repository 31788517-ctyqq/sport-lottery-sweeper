import requests
import json
from datetime import datetime

def test_create_data_source_with_type():
    # 测试创建数据源，包含type字段
    url = "http://localhost:8001/api/v1/admin/sources"
    
    # 使用时间戳确保名称唯一
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"测试数据源_{timestamp}"
    
    # 准备测试数据 - 包含type字段
    payload = {
        "name": name,
        "type": "api",  # 明确指定类型
        "status": "online",
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
                print(f"   类型: {result['data']['type']}")
            else:
                print(f"❌ 数据源创建失败: {result.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求过程中发生错误: {e}")

if __name__ == "__main__":
    test_create_data_source_with_type()