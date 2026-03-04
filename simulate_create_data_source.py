import requests
import json
from datetime import datetime

# 创建数据源
def create_data_source():
    url = "http://127.0.0.1:8000/api/v1/admin/sources"
    
    # 使用当前时间戳创建唯一名称
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    name = f"测试数据源-{timestamp}"
    
    # 模拟创建一个数据源
    payload = {
        "name": name,
        "type": "api",
        "url": "https://api.example.com/test",
        "config": {
            "method": "GET",
            "timeout": 30,
            "headers": {
                "User-Agent": "Mozilla/5.0 (compatible; TestBot/1.0)"
            },
            "description": "这是一个测试数据源，用于验证创建功能",
            "category": "match_data",
            "auto_crawl": True,
            "crawl_interval": 300,
            "priority": "medium"
        },
        "status": True
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"创建数据源响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"创建成功: {result}")
            return result.get('data', {}).get('id')
        else:
            print(f"创建失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return None

# 查询数据源列表
def get_data_source_list():
    url = "http://127.0.0.1:8000/api/v1/admin/sources?page=1&size=100"
    
    try:
        response = requests.get(url)
        print(f"获取数据源列表响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"数据源总数: {result.get('data', {}).get('total', 0)}")
            items = result.get('data', {}).get('items', [])
            
            print("\n数据源列表 (最近5条):")
            for idx, item in enumerate(items[:5], 1):
                print(f"{idx}. ID: {item.get('id')}, Name: {item.get('name')}, Source ID: {item.get('source_id')}")
                
            return items
        else:
            print(f"获取列表失败: {response.text}")
            return []
            
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return []

if __name__ == "__main__":
    print("=== 开始模拟创建数据源 ===")
    
    # 创建数据源
    source_id = create_data_source()
    
    if source_id:
        print(f"\n成功创建数据源，ID: {source_id}")
        
        # 获取数据源列表
        print("\n=== 获取数据源列表 ===")
        data_sources = get_data_source_list()
        
        # 检查新创建的数据源是否在列表中
        new_source = next((ds for ds in data_sources if ds.get('id') == source_id), None)
        if new_source:
            print(f"\n✅ 成功在列表中找到新创建的数据源:")
            print(f"   ID: {new_source.get('id')}")
            print(f"   Name: {new_source.get('name')}")
            print(f"   Source ID: {new_source.get('source_id')}")
            
            # 检查是否正确生成了source_id
            expected_source_id = f"DS{source_id:03d}"
            actual_source_id = new_source.get('source_id')
            if actual_source_id == expected_source_id:
                print(f"   ✅ Source ID 正确生成: {actual_source_id}")
            else:
                print(f"   ❌ Source ID 未正确生成，期望: {expected_source_id}，实际: {actual_source_id}")
        else:
            print(f"\n❌ 未能在列表中找到新创建的数据源")
    else:
        print("\n❌ 创建数据源失败")