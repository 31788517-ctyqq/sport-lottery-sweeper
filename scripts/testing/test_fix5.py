import requests
import json

# 测试创建数据源时无效的status值
def test_create_source_invalid_status():
    url = "http://localhost:8000/api/v1/admin/sources"
    
    # 测试: status为无效值
    data = {
        "name": "测试无效状态",
        "type": "api",
        "url": "https://example.com/api",
        "status": "invalid_status",
        "config": json.dumps({"category": "match_data"}),
        "remark": "测试无效状态值"
    }
    
    print("测试无效status值")
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")

# 测试创建数据源时status为null
def test_create_source_null_status():
    url = "http://localhost:8000/api/v1/admin/sources"
    
    data = {
        "name": "测试null状态",
        "type": "api",
        "url": "https://example.com/api",
        "status": None,
        "config": json.dumps({"category": "match_data"}),
        "remark": "测试null状态"
    }
    
    print("\n测试null status值")
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")

# 测试100qiu数据源无效status
def test_100qiu_invalid_status():
    url = "http://localhost:8000/api/v1/data-source-100qiu/"
    
    data = {
        "name": "100qiu无效状态测试",
        "url": "https://m.100qiu.com/api/dcListBasic",
        "date_time": "latest",
        "update_frequency": 60,
        "field_mapping": {},
        "status": "invalid_status"
    }
    
    print("\n测试100qiu数据源无效status")
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    print("测试数据源API的无效status处理...")
    test_create_source_invalid_status()
    test_create_source_null_status()
    test_100qiu_invalid_status()