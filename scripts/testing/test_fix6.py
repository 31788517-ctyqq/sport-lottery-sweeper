import requests
import json

# 测试创建数据源时空名称
def test_create_source_empty_name():
    url = "http://localhost:8000/api/v1/admin/sources"
    
    # 测试: 空名称
    data = {
        "name": "",
        "type": "api",
        "url": "https://example.com/api",
        "status": "online",
        "config": json.dumps({"category": "match_data"}),
        "remark": "测试空名称"
    }
    
    print("测试空名称")
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")

# 测试创建数据源时缺少type字段
def test_create_source_no_type():
    url = "http://localhost:8000/api/v1/admin/sources"
    
    data = {
        "name": "测试无类型",
        "url": "https://example.com/api",
        "status": "online",
        "config": json.dumps({"category": "match_data"}),
        "remark": "测试无类型"
    }
    
    print("\n测试缺少type字段")
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    print("测试数据源API的空名称处理...")
    test_create_source_empty_name()
    test_create_source_no_type()