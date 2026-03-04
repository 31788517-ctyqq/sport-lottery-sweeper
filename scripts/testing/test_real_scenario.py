import requests
import json
from datetime import datetime

def test_real_scenario():
    # 模拟前端发送的真实请求
    url = "http://localhost:8001/api/v1/admin/sources"
    
    # 模拟前端表单数据
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload = {
        "name": f"100qiu{timestamp}",
        "type": "api",
        "status": "online",
        "url": f"https://m.100qiu.com/api/dcListBasic?dateTime={timestamp}",
        "config": {
            "method": "GET",
            "timeout": 30,
            "headers": {
                "User-Agent": "Mozilla/5.0 (compatible; TestBot/1.0)",
                "Accept": "application/json"
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
                print(f"   配置: {result['data']['config']}")
            else:
                print(f"❌ 数据源创建失败: {result.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求过程中发生错误: {e}")

if __name__ == "__main__":
    test_real_scenario()