"""
API端点测试脚本
测试实体映射和官方信息管理功能
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001/api/v1"

def test_get_team_mappings():
    """测试获取球队映射配置"""
    print("测试获取球队映射配置...")
    try:
        response = requests.get(f"{BASE_URL}/entity-mapping/mappings/team")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功获取球队映射配置，共 {len(data['data'])} 条记录")
            # 打印前3条记录作为示例
            for i, (team_id, team_data) in enumerate(list(data['data'].items())[:3]):
                print(f"   {team_id}: {team_data.get('zh', ['N/A'])}")
        else:
            print(f"❌ 获取球队映射配置失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")


def test_get_league_mappings():
    """测试获取联赛映射配置"""
    print("\n测试获取联赛映射配置...")
    try:
        response = requests.get(f"{BASE_URL}/entity-mapping/mappings/league")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功获取联赛映射配置，共 {len(data['data'])} 条记录")
            # 打印前3条记录作为示例
            for i, (league_id, league_data) in enumerate(list(data['data'].items())[:3]):
                print(f"   {league_id}: {league_data.get('zh', ['N/A'])}")
        else:
            print(f"❌ 获取联赛映射配置失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")


def test_standardize_match_data():
    """测试比赛数据标准化功能"""
    print("\n测试比赛数据标准化功能...")
    try:
        raw_data = {
            "home_team": "皇家马德里",
            "away_team": "巴塞罗那",
            "league": "西甲联赛",
            "match_time": "2026-03-15T20:00:00",
            "odds": {"home": 1.8, "draw": 3.2, "away": 4.0}
        }
        response = requests.post(
            f"{BASE_URL}/entity-mapping/matches/standardize?source_id=sports_data_api",
            json=raw_data
        )
        if response.status_code == 200:
            result = response.json()
            standardized = result["standardized_data"]
            print(f"✅ 数据标准化成功")
            print(f"   主队: {standardized['home_team_id']}")
            print(f"   客队: {standardized['away_team_id']}")
            print(f"   联赛: {standardized['league_id']}")
        else:
            print(f"❌ 数据标准化失败，状态码: {response.status_code}")
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")


def test_get_official_info_summary():
    """测试获取官方信息验证摘要"""
    print("\n测试获取官方信息验证摘要...")
    try:
        response = requests.get(f"{BASE_URL}/entity-mapping/official-info/summary")
        if response.status_code == 200:
            data = response.json()
            summary = data["data"]["summary"]
            print(f"✅ 成功获取官方信息验证摘要")
            print(f"   总计: {summary['total']}")
            print(f"   有效: {summary['valid']}")
            print(f"   无效: {summary['invalid']}")
            print(f"   需更新: {summary['needs_update']}")
        else:
            print(f"❌ 获取官方信息验证摘要失败，状态码: {response.status_code}")
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")


def test_system_health():
    """测试系统健康状态"""
    print("\n测试系统健康状态...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 系统健康状态正常")
            print(f"   状态: {data['status']}")
            print(f"   版本: {data['version']}")
        else:
            print(f"⚠️ 系统健康状态检查失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"⚠️ 请求失败 (可能该端点不存在): {e}")


if __name__ == "__main__":
    print("开始API端点冒烟测试...\n")
    
    # 等待服务启动
    time.sleep(2)
    
    test_system_health()
    test_get_team_mappings()
    test_get_league_mappings()
    test_standardize_match_data()
    test_get_official_info_summary()
    
    print("\nAPI端点冒烟测试完成!")
#!/usr/bin/env python
"""
Test script to verify API endpoints are working properly
"""
import requests
import sys

def test_api_endpoints():
    base_url = "http://localhost:8000"
    
    print("Testing API endpoints...")
    
    # Test data-source-100qiu endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/data-source-100qiu/latest-matches?limit=5&include_raw=true")
        print(f"✓ /api/v1/data-source-100qiu/latest-matches: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
        else:
            print(f"  Error: {response.text[:200]}")
    except Exception as e:
        print(f"✗ /api/v1/data-source-100qiu/latest-matches: Error - {e}")
    
    # Test beidan-filter statistics endpoint
    try:
        payload = {}
        response = requests.post(f"{base_url}/api/v1/beidan-filter/statistics", json=payload)
        print(f"✓ /api/v1/beidan-filter/statistics: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
        elif response.status_code == 422:
            print("  Note: 422 status likely due to validation error with empty payload, which is expected")
        else:
            print(f"  Error: {response.text[:200]}")
    except Exception as e:
        print(f"✗ /api/v1/beidan-filter/statistics: Error - {e}")

    # Test date-time-options endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/data-source-100qiu/date-time-options")
        print(f"✓ /api/v1/data-source-100qiu/date-time-options: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
        else:
            print(f"  Error: {response.text[:200]}")
    except Exception as e:
        print(f"✗ /api/v1/data-source-100qiu/date-time-options: Error - {e}")

if __name__ == "__main__":
    test_api_endpoints()