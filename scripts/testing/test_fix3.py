import requests
import json

# 测试创建数据源时config字段为无效JSON
def test_create_source_invalid_config():
    url = "http://localhost:8000/api/v1/admin/sources"
    
    # 测试: config字段为无效JSON字符串
    data = {
        "name": "测试无效配置",
        "type": "api",
        "url": "https://example.com/api",
        "status": "online",
        "config": "{invalid json",
        "remark": "测试无效JSON配置"
    }
    
    print("测试无效JSON配置")
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        # 检查响应格式
        if response.status_code == 200:
            result = response.json()
            print(f"成功: {result.get('success')}")
            print(f"消息: {result.get('message')}")
            print(f"错误代码: {result.get('error', {}).get('code')}")
    except Exception as e:
        print(f"请求异常: {e}")

# 测试创建数据源时config字段为空字符串
def test_create_source_empty_config():
    url = "http://localhost:8000/api/v1/admin/sources"
    
    data = {
        "name": "测试空配置",
        "type": "api",
        "url": "https://example.com/api",
        "status": "online",
        "config": "",
        "remark": "测试空配置"
    }
    
    print("\n测试空配置字符串")
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")

# 测试创建数据源时缺少config字段
def test_create_source_no_config():
    url = "http://localhost:8000/api/v1/admin/sources"
    
    data = {
        "name": "测试无配置",
        "type": "api",
        "url": "https://example.com/api",
        "status": "online",
        "remark": "测试无配置字段"
    }
    
    print("\n测试缺少config字段")
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    print("测试数据源API的config字段处理...")
    test_create_source_invalid_config()
    test_create_source_empty_config()
    test_create_source_no_config()