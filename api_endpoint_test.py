"""
API端点验证脚本
验证实体映射和官方信息管理功能的API端点是否已正确注册
"""

import time
import requests
from threading import Thread


def check_api_endpoints():
    """检查API端点是否可用"""
    base_url = "http://localhost:8002"
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(8)
    
    endpoints_to_test = [
        ("/api/v1/entity-mapping/mappings/team", "获取球队映射"),
        ("/api/v1/entity-mappings/mappings/league", "获取联赛映射"),
        ("/api/v1/entity-mapping/matches/standardize", "标准化比赛数据"),
        ("/api/v1/entity-mapping/official-info/summary", "官方信息验证摘要"),
    ]
    
    print("\n开始测试API端点...")
    
    for endpoint, description in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code in [200, 405]:  # 405表示端点存在但方法不正确
                print(f"✅ {description}: {endpoint} - 存在 (状态码: {response.status_code})")
            else:
                print(f"❌ {description}: {endpoint} - 不存在 (状态码: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print(f"❌ {description}: {endpoint} - 连接失败")
        except requests.exceptions.Timeout:
            print(f"⚠️  {description}: {endpoint} - 请求超时")
        except Exception as e:
            print(f"❌ {description}: {endpoint} - 错误: {e}")


def test_specific_functionality():
    """测试具体功能"""
    base_url = "http://localhost:8002"
    
    print("\n测试具体功能...")
    
    # 测试获取球队映射
    try:
        response = requests.get(f"{base_url}/api/v1/entity-mapping/mappings/team", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print("✅ 球队映射获取成功")
                print(f"   映射数量: {len(data.get('data', {}))}")
            else:
                print("⚠️ 球队映射返回格式不符合预期")
        else:
            print(f"❌ 球队映射请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 球队映射测试异常: {e}")
    
    # 测试数据标准化
    try:
        test_data = {
            "home_team": "皇家马德里",
            "away_team": "巴塞罗那", 
            "match_time": "2026-03-15T20:00:00",
            "source_id": "test_source"
        }
        response = requests.post(
            f"{base_url}/api/v1/entity-mapping/matches/standardize?source_id=test_source",
            json=test_data,
            timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            if "standardized_data" in result:
                print("✅ 数据标准化功能正常")
                std_data = result["standardized_data"]
                print(f"   标准化结果: {std_data.get('home_team_id')} vs {std_data.get('away_team_id')}")
            else:
                print("⚠️ 数据标准化返回格式不符合预期")
        else:
            print(f"❌ 数据标准化请求失败: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"❌ 数据标准化测试异常: {e}")


if __name__ == "__main__":
    print("开始API端点验证...")
    
    # 启动测试
    check_api_endpoints()
    test_specific_functionality()
    
    print("\nAPI端点验证完成!")