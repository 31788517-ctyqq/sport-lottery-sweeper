import requests
import json
from datetime import datetime

def test_create_data_source_detailed():
    # 测试创建数据源，获取详细的错误信息
    url = "http://localhost:8001/api/v1/admin/sources"
    
    # 使用时间戳确保名称唯一
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"测试数据源_{timestamp}"
    
    # 准备测试数据 - 匹配后端API参数要求
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
        
        if response.status_code == 422:
            print("❌ 遇到422验证错误，这通常意味着请求参数格式不正确")
            print("检查API参数定义是否与后端要求一致")
        elif response.status_code == 200:
            print("✅ 数据源创建成功!")
        else:
            print(f"❌ 其他错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求过程中发生错误: {e}")

if __name__ == "__main__":
    test_create_data_source_detailed()