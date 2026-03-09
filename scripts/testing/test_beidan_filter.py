"""
测试北单过滤功能
"""

import requests
import sys
import os

# 添加后端路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.utils.mock_data_generator import generate_mock_beidan_matches
from backend.app.services.filter_engine import BeidanFilterEngine
from backend.app.utils.data_processor import transform_multiple_beidan_matches


def test_mock_data_generation():
    """测试模拟数据生成"""
    print("=== 测试模拟数据生成 ===")
    matches = generate_mock_beidan_matches(5)
    
    print(f"生成了 {len(matches)} 条模拟数据:")
    for i, match in enumerate(matches):
        print(f"  {i+1}. ID: {match['id']}, Teams: {match['homeTeam']} vs {match['guestTeam']}")
        print(f"     Power: {match['homePower']} vs {match['guestPower']}")
        print(f"     WinPan: {match['homeWinPan']} vs {match['guestWinPan']}")
        print(f"     RQ: {match['rq']}")
    print()


def test_filter_engine():
    """测试筛选引擎"""
    print("=== 测试筛选引擎 ===")
    engine = BeidanFilterEngine()
    
    # 生成一些模拟数据
    matches = generate_mock_beidan_matches(10)
    
    # 批量转换数据
    transformed_matches = transform_multiple_beidan_matches(matches)
    
    # 转换为内部模型
    match_models = []
    for transformed_data in transformed_matches:
        match_model = BeidanFilterEngine().transform_beidan_match(transformed_data)
        match_models.append(match_model)
    
    print(f"转换了 {len(match_models)} 条数据到内部模型")
    
    # 测试筛选
    filters = {
        'strength': ['1', '2'],  # 主队微优或强力压制
        'winLevel': ['1', '2', '3'],  # 主队有利
        'stability': ['S', 'A', 'B'],  # 高稳定性
        'source': 'beidan'
    }
    
    filtered_matches = engine.apply_filters(match_models, filters)
    
    print(f"应用筛选后剩余 {len(filtered_matches)} 条数据")
    
    for match in filtered_matches[:3]:  # 只显示前3条
        print(f"  ID: {match.id}, Teams: {match.teams}")
        print(f"     Strength: {match.strength}, WinLevel: {match.winLevel}, Stability: {match.stability}")
        print(f"     Tier: {match.tier}, Warning: {match.warning}")
    
    print()


def test_api_endpoints():
    """测试API端点"""
    print("=== 测试API端点 ===")
    
    base_url = "http://localhost:8000"
    
    # 测试选项API
    try:
        response = requests.get(f"{base_url}/api/v1/beidan-filter/options")
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                print("✓ 选项API正常工作")
                print(f"  Strength选项数: {len(data['data']['strength'])}")
                print(f"  WinLevel选项数: {len(data['data']['winLevel'])}")
                print(f"  Stability选项数: {len(data['data']['stability'])}")
            else:
                print(f"✗ 选项API返回非预期数据: {data}")
        else:
            print(f"✗ 选项API返回错误状态码: {response.status_code}")
            print(f"  响应内容: {response.text}")
    except Exception as e:
        print(f"✗ 选项API测试失败: {e}")
    
    # 测试筛选API
    try:
        payload = {
            "strength": ["1", "2"],
            "winLevel": ["1", "2", "3"],
            "stability": ["S", "A", "B"]
        }
        
        response = requests.post(f"{base_url}/api/v1/beidan-filter", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                print("✓ 筛选API正常工作")
                print(f"  筛选结果数: {data['data']['stats']['total']}")
                print(f"  按P级分布: {data['data']['stats']['byTier']}")
            else:
                print(f"✗ 筛选API返回非预期数据: {data}")
        else:
            print(f"✗ 筛选API返回错误状态码: {response.status_code}")
            print(f"  响应内容: {response.text}")
    except Exception as e:
        print(f"✗ 筛选API测试失败: {e}")
    
    # 测试真实数据API
    try:
        response = requests.get(f"{base_url}/api/v1/beidan-filter/real-data")
        if response.status_code == 200:
            data = response.json()
            print("✓ 真实数据API正常工作")
            print(f"  状态码: {data.get('code')}")
            print(f"  消息: {data.get('message')}")
        else:
            print(f"✗ 真实数据API返回错误状态码: {response.status_code}")
            print(f"  响应内容: {response.text}")
    except Exception as e:
        print(f"✗ 真实数据API测试失败: {e}")
    
    print()


def main():
    print("开始测试北单过滤功能...\n")
    
    test_mock_data_generation()
    test_filter_engine()
    test_api_endpoints()
    
    print("测试完成!")


if __name__ == "__main__":
    main()