"""
验证100qiu数据源是否正确显示在API响应中
"""
import requests
import json

def verify_data_source():
    base_url = "http://localhost:8000"
    
    print("="*60)
    print("验证100qiu数据源是否正确显示")
    print("="*60)
    
    # 测试数据源API
    print("\n1. 测试数据源API: /api/v1/admin/sources")
    try:
        response = requests.get(f"{base_url}/api/v1/admin/sources")
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   响应数据结构: {list(data.keys())}")
            
            items = data.get('data', {}).get('items', [])
            print(f"   数据源总数: {len(items)}")
            
            print("\n   数据源列表:")
            for i, item in enumerate(items, 1):
                print(f"   {i}. 名称: {item.get('name', 'N/A')}")
                print(f"      类型: {item.get('type', 'N/A')}")
                print(f"      URL: {item.get('url', 'N/A')}")
                print(f"      ID: {item.get('id', 'N/A')}")
                print(f"      状态: {'激活' if item.get('status', False) else '未激活'}")
                print()
                
                # 检查是否包含100qiu数据源
                if "100qiu" in item.get('name', ''):
                    print(f"✅ 找到100qiu数据源: {item['name']}")
                    print(f"   ID: {item['id']}")
                    print(f"   URL: {item['url']}")
                    print(f"   类型: {item['type']}")
                    
            # 检查特定数据源
            qiu_sources = [item for item in items if "100qiu" in item.get('name', '')]
            if qiu_sources:
                print(f"\n✅ 验证成功: 发现 {len(qiu_sources)} 个100qiu相关数据源")
            else:
                print(f"\n❌ 验证失败: 未找到100qiu相关数据源")
                
        else:
            print(f"   响应: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n" + "="*60)
    print("验证完成")
    print("="*60)

if __name__ == "__main__":
    verify_data_source()