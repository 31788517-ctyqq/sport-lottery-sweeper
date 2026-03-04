"""
测试分类筛选功能
"""
import json
import requests
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_category_filter():
    """测试分类筛选功能"""
    base_url = "http://localhost:8001/api/v1/admin/sources"  # 更新为正确的API路径
    
    print("正在测试分类筛选功能...")
    
    # 测试按分类筛选 - 比赛数据
    try:
        print("\n1. 测试按分类='match_data'筛选:")
        response = requests.get(base_url, params={
            "category": "match_data",  # 这是我们要测试的分类
            "page": 1,
            "size": 10
        })
        
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                items = data.get('data', {}).get('items', [])
                print(f"   按分类筛选找到 {len(items)} 条匹配记录")
                
                if len(items) > 0:
                    print("   匹配的记录:")
                    for item in items:
                        print(f"     - ID: {item.get('id')}, Name: {item.get('name')}, Category: {extract_category_from_config(item.get('config'))}")
                else:
                    print("   没有找到匹配的记录，因为数据源配置中没有category字段")
            else:
                print(f"   请求失败: {data.get('message', 'Unknown error')}")
        else:
            print(f"   请求失败，状态码: {response.status_code}")
            
        # 测试按其他筛选条件（如源ID）是否正常工作
        print("\n2. 测试按源ID='DS009'筛选:")
        response = requests.get(base_url, params={
            "source_id": "DS009",
            "page": 1,
            "size": 10
        })
        
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                items = data.get('data', {}).get('items', [])
                print(f"   按源ID筛选找到 {len(items)} 条匹配记录")
                
                if len(items) > 0:
                    print("   匹配的记录:")
                    for item in items:
                        print(f"     - ID: {item.get('id')}, Name: {item.get('name')}, Source ID: {item.get('source_id')}")
                else:
                    print("   没有找到源ID为'DS009'的记录")
            else:
                print(f"   请求失败: {data.get('message', 'Unknown error')}")
        else:
            print(f"   请求失败，状态码: {response.status_code}")
            
        # 获取一些数据源来查看其配置结构
        print("\n3. 获取部分数据源查看配置结构:")
        response = requests.get(base_url, params={"size": 5})
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                items = data.get('data', {}).get('items', [])
                print(f"   获取到 {len(items)} 条记录用于分析配置结构")
                
                for idx, item in enumerate(items, 1):
                    print(f"     {idx}. ID: {item.get('id')}, Name: {item.get('name')}")
                    print(f"        Config: {json.dumps(item.get('config'), ensure_ascii=False)}")
                    print(f"        Category in config: {extract_category_from_config(item.get('config'))}")
            else:
                print(f"   获取数据失败: {data.get('message', 'Unknown error')}")
        else:
            print(f"   获取数据失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"   测试过程中发生错误: {str(e)}")
        print(f"   请确保后端服务 (localhost:8001) 正在运行")


def extract_category_from_config(config):
    """从配置中提取分类信息"""
    if isinstance(config, dict):
        return config.get('category', 'Not found')
    elif isinstance(config, str):
        try:
            parsed = json.loads(config)
            return parsed.get('category', 'Not found in JSON')
        except:
            return 'Invalid JSON'
    else:
        return 'No config'


if __name__ == "__main__":
    test_category_filter()