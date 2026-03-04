import requests
import json

# 测试创建数据源时空分类
def test_create_source_empty_category():
    url = "http://localhost:8000/api/v1/admin/sources"
    
    # 测试: 空分类字符串
    data = {
        "name": "测试空分类",
        "type": "api",
        "url": "https://example.com/api",
        "status": "online",
        "config": json.dumps({"category": ""}),
        "remark": "测试空分类",
        "category": ""
    }
    
    print("测试空分类")
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")

# 测试更新数据源
def test_update_source():
    # 先创建一个数据源
    create_url = "http://localhost:8000/api/v1/admin/sources"
    create_data = {
        "name": "更新测试数据源",
        "type": "api",
        "url": "https://example.com/api",
        "status": "online",
        "config": json.dumps({"category": "match_data"}),
        "remark": "用于更新测试"
    }
    
    print("\n测试更新数据源")
    try:
        create_response = requests.post(create_url, json=create_data)
        if create_response.status_code == 200:
            result = create_response.json()
            if result.get('success'):
                source_id = result.get('data', {}).get('id')
                print(f"创建的数据源ID: {source_id}")
                
                # 现在更新它
                update_url = f"http://localhost:8000/api/v1/admin/sources/{source_id}"
                update_data = {
                    "name": "更新后的名称",
                    "status": "offline",
                    "category": "news"
                }
                
                update_response = requests.put(update_url, json=update_data)
                print(f"更新状态码: {update_response.status_code}")
                print(f"更新响应: {update_response.text}")
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    print("测试数据源API的空分类处理...")
    test_create_source_empty_category()
    test_update_source()