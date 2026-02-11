"""
测试API筛选功能
"""
import requests
import json

def test_api_filter():
    """测试API筛选功能"""
    base_url = "http://localhost:8001/api/v1/admin/sources"
    
    print("测试API筛选功能...")
    
    # 测试无筛选条件
    print("\n1. 测试无筛选条件:")
    response = requests.get(base_url, params={"page": 1, "size": 20})
    if response.status_code == 200:
        data = response.json()
        print(f"   总记录数: {data['data']['total']}")
        print(f"   返回记录数: {len(data['data']['items'])}")
    else:
        print(f"   请求失败: {response.status_code}")
    
    # 测试分类筛选
    print("\n2. 测试分类筛选 (category=match_data):")
    response = requests.get(base_url, params={"category": "match_data", "page": 1, "size": 20})
    if response.status_code == 200:
        data = response.json()
        print(f"   总记录数: {data['data']['total']}")
        print(f"   返回记录数: {len(data['data']['items'])}")
        print("   返回的记录:")
        for item in data['data']['items']:
            config = item.get('config', {})
            category = config.get('category', 'Not found')
            print(f"     - ID: {item['id']}, Name: {item['name']}, Category: {category}")
    else:
        print(f"   请求失败: {response.status_code}")
    
    # 测试源ID筛选
    print("\n3. 测试源ID筛选 (source_id=DS009):")
    response = requests.get(base_url, params={"source_id": "DS009", "page": 1, "size": 20})
    if response.status_code == 200:
        data = response.json()
        print(f"   总记录数: {data['data']['total']}")
        print(f"   返回记录数: {len(data['data']['items'])}")
        print("   返回的记录:")
        for item in data['data']['items']:
            print(f"     - ID: {item['id']}, Name: {item['name']}, Source ID: {item['source_id']}")
    else:
        print(f"   请求失败: {response.status_code}")

    # 测试名称搜索
    print("\n4. 测试名称搜索 (name=测试):")
    response = requests.get(base_url, params={"search": "测试", "page": 1, "size": 20})
    if response.status_code == 200:
        data = response.json()
        print(f"   总记录数: {data['data']['total']}")
        print(f"   返回记录数: {len(data['data']['items'])}")
        print("   返回的记录:")
        for item in data['data']['items']:
            print(f"     - ID: {item['id']}, Name: {item['name']}")
    else:
        print(f"   请求失败: {response.status_code}")

if __name__ == "__main__":
    test_api_filter()