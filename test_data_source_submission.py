#!/usr/bin/env python3
"""
测试数据源表单提交API
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_regular_data_source_create():
    """测试普通数据源创建"""
    print("测试普通数据源创建...")
    
    data = {
        "name": "测试数据源API",
        "type": "api",
        "url": "https://api.example.com/data",
        "status": "online",
        "config": json.dumps({"category": "match_data"}),
        "remark": "测试备注"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/admin/sources", json=data, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"成功: {result.get('success')}")
            print(f"消息: {result.get('message')}")
            return True
        else:
            print(f"错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"请求异常: {e}")
        return False

def test_100qiu_data_source_create():
    """测试100qiu数据源创建"""
    print("\n测试100qiu数据源创建...")
    
    data = {
        "name": "100qiu测试数据源",
        "url": "https://m.100qiu.com/api/dcListBasic",
        "date_time": "latest",
        "update_frequency": 60,
        "field_mapping": {},
        "status": "online"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/data-source-100qiu/", json=data, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"ID: {result.get('id')}")
            print(f"名称: {result.get('name')}")
            return True
        else:
            print(f"错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"请求异常: {e}")
        return False

def test_frontend_format():
    """测试前端发送的格式（模拟前端请求）"""
    print("\n测试前端发送的格式...")
    
    # 模拟前端提交的数据格式
    config_obj = {"category": "match_data"}
    submit_data = {
        "name": "前端格式测试",
        "type": "api",
        "url": "https://api.example.com/test",
        "status": "online",
        "config": json.dumps(config_obj),
        "remark": "前端测试备注"
    }
    
    # 对于100qiu数据源，前端还会添加额外字段
    data_100qiu = {
        **submit_data,
        "date_time": "latest",
        "update_frequency": 60,
        "field_mapping": {}
    }
    
    print("普通数据源格式:")
    print(json.dumps(submit_data, indent=2, ensure_ascii=False))
    
    print("\n100qiu数据源格式:")
    print(json.dumps(data_100qiu, indent=2, ensure_ascii=False))
    
    # 测试普通API
    print("\n发送到普通API...")
    try:
        response = requests.post(f"{BASE_URL}/admin/sources", json=submit_data, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")
    
    # 测试100qiu API（可能会失败，因为有多余字段）
    print("\n发送到100qiu API...")
    try:
        response = requests.post(f"{BASE_URL}/data-source-100qiu/", json=data_100qiu, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("数据源表单提交API测试")
    print("=" * 60)
    
    # test_regular_data_source_create()
    # test_100qiu_data_source_create()
    test_frontend_format()