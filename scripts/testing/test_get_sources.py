import requests
import json

def test_get_sources():
    # 测试获取数据源列表
    url = "http://localhost:8001/api/v1/admin/sources?page=1&size=20"
    
    print("发送获取数据源列表请求...")
    print(f"请求URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ 数据源列表获取成功! 共 {result['data']['total']} 条记录")
                print(f"   当前页数量: {len(result['data']['items'])}")
            else:
                print(f"❌ 数据源列表获取失败: {result.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求过程中发生错误: {e}")

if __name__ == "__main__":
    test_get_sources()