"""
测试前端筛选功能
"""
import requests
import json

def test_frontend_filter():
    """测试前端筛选功能"""
    base_url = "http://localhost:8001/api/v1/admin/sources"
    
    print("测试前端筛选功能...")
    
    # 测试分类筛选 - 比赛数据
    print("\n1. 测试分类筛选 (category=match_data - 比赛数据):")
    response = requests.get(base_url, params={
        "category": "match_data", 
        "page": 1, 
        "size": 20
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"   总记录数: {data['data']['total']}")
        print(f"   返回记录数: {len(data['data']['items'])}")
        
        if data['data']['items']:
            print("   返回的记录:")
            for item in data['data']['items']:
                config = item.get('config', {})
                category = config.get('category', 'Not found')
                print(f"     - ID: {item['id']}, Name: {item['name']}, Category: {category}")
        else:
            print("   没有返回任何记录")
    else:
        print(f"   请求失败: {response.status_code}, {response.text}")
    
    # 测试所有分类选项
    categories = [
        ("match_data", "比赛数据"),
        ("player_info", "球员信息"),
        ("team_info", "球队信息"),
        ("odds_data", "赔率数据"),
        ("news", "新闻资讯"),
        ("euro_odds", "欧洲赔率"),
        ("asia_handicap", "亚洲盘口"),
        ("over_under", "大小球"),
        ("goals", "进球数")
    ]
    
    print(f"\n2. 测试所有分类选项:")
    for cat_value, cat_label in categories:
        response = requests.get(base_url, params={
            "category": cat_value, 
            "page": 1, 
            "size": 20
        })
        
        if response.status_code == 200:
            data = response.json()
            count = data['data']['total']
            print(f"   {cat_label} ({cat_value}): {count} 条记录")
        else:
            print(f"   {cat_label} ({cat_value}): 请求失败")
    
    # 测试无筛选条件
    print(f"\n3. 测试无筛选条件:")
    response = requests.get(base_url, params={"page": 1, "size": 20})
    if response.status_code == 200:
        data = response.json()
        print(f"   总记录数: {data['data']['total']}")
        print(f"   返回记录数: {len(data['data']['items'])}")
    else:
        print(f"   请求失败: {response.status_code}")

if __name__ == "__main__":
    test_frontend_filter()