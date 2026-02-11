"""
测试数据源按source_id筛选功能
"""
import requests
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_source_id_filter():
    """测试按source_id筛选功能"""
    base_url = "http://localhost:8000/api/admin/v1"
    
    # 首先获取所有数据源，看看是否存在DS009
    print("获取所有数据源...")
    try:
        response = requests.get(f"{base_url}/sources", params={"size": 100})
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"总共找到 {data.get('data', {}).get('total', 0)} 个数据源")
        
        # 检查是否存在DS009
        items = data.get('data', {}).get('items', [])
        ds009_found = False
        for item in items:
            if item.get('source_id') == 'DS009':
                print(f"找到了DS009: {item}")
                ds009_found = True
                break
        
        if not ds009_found:
            print("在数据源列表中未找到DS009")
        
        # 测试按source_id筛选
        print("\n测试按source_id=DS009筛选...")
        response = requests.get(f"{base_url}/sources", params={
            "source_id": "DS009",
            "page": 1,
            "size": 10
        })
        
        print(f"筛选请求状态码: {response.status_code}")
        if response.status_code == 200:
            filter_data = response.json()
            print(f"筛选结果: {filter_data}")
            
            if filter_data.get('success'):
                filtered_items = filter_data.get('data', {}).get('items', [])
                print(f"筛选到 {len(filtered_items)} 条记录")
                
                if len(filtered_items) > 0:
                    print("筛选功能正常工作！")
                    for item in filtered_items:
                        print(f"- {item.get('source_id')}: {item.get('name')}")
                else:
                    print("筛选功能返回了空结果，可能数据中不存在DS009")
            else:
                print(f"筛选请求失败: {filter_data.get('message', 'Unknown error')}")
        else:
            print(f"筛选请求失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")


if __name__ == "__main__":
    test_source_id_filter()