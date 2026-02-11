import requests
import json

# 测试创建数据源时缺少必需字段
def test_create_source_missing_fields():
    url = "http://localhost:8000/api/v1/admin/sources"
    
    # 测试1: 缺少name字段
    data1 = {
        "type": "api",
        "url": "https://example.com/api",
        "status": "online"
    }
    
    print("测试1: 缺少name字段")
    try:
        response = requests.post(url, json=data1)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")
    
    # 测试2: 无效的type字段
    data2 = {
        "name": "测试数据源2",
        "type": "invalid_type",
        "url": "https://example.com/api",
        "status": "online"
    }
    
    print("\n测试2: 无效的type字段")
    try:
        response = requests.post(url, json=data2)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")
    
    # 测试3: 无效的URL格式
    data3 = {
        "name": "测试数据源3",
        "type": "api",
        "url": "invalid_url",
        "status": "online"
    }
    
    print("\n测试3: 无效的URL格式")
    try:
        response = requests.post(url, json=data3)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")

# 测试100qiu数据源API
def test_100qiu_api():
    url = "http://localhost:8000/api/v1/data-source-100qiu/"
    
    data = {
        "name": "100qiu测试数据源",
        "url": "https://m.100qiu.com/api/dcListBasic",
        "date_time": "latest",
        "update_frequency": 60,
        "field_mapping": {},
        "status": "online"
    }
    
    print("\n测试100qiu数据源创建")
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    print("测试数据源API验证错误...")
    test_create_source_missing_fields()
    test_100qiu_api()