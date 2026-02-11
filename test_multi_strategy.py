#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试多策略筛选功能
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_multi_strategy_info():
    """测试多策略功能信息接口"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/multi-strategy/")
        print(f"多策略功能信息 - 状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"请求失败: {e}")

def test_get_strategies():
    """测试获取可用策略接口"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/multi-strategy/strategies")
        print(f"获取策略列表 - 状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

def test_manual_execution():
    """测试手动执行多策略筛选"""
    try:
        payload = {
            "strategy_ids": ["high_probability_winning", "balanced_odds"],
            "message_format": "table"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/multi-strategy/execute",
            json=payload
        )
        print(f"手动执行多策略 - 状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)[:500]}...")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    print("开始测试多策略筛选功能...")
    print("="*50)
    
    print("\n1. 测试多策略功能信息接口:")
    test_multi_strategy_info()
    
    print("\n2. 测试获取可用策略接口:")
    test_get_strategies()
    
    print("\n3. 测试手动执行多策略筛选:")
    test_manual_execution()
    
    print("\n测试完成!")