#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整测试多策略筛选功能
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_multi_strategy_info():
    """测试多策略功能信息接口"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/multi-strategy/")
        print(f"✓ 多策略功能信息 - 状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  - 消息: {data.get('message')}")
            print(f"  - 特性数量: {len(data.get('features', []))}")
        else:
            print(f"  - 错误响应: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False

def test_get_strategies():
    """测试获取可用策略接口"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/multi-strategy/strategies")
        print(f"✓ 获取策略列表 - 状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            strategies = data.get('data', [])
            print(f"  - 可用策略数量: {len(strategies)}")
            print(f"  - 策略列表: {strategies}")
        else:
            print(f"  - 错误响应: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False

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
        print(f"✓ 手动执行多策略 - 状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  - 执行状态: {'成功' if data.get('success') else '失败'}")
            print(f"  - 消息: {data.get('message')}")
            print(f"  - 结果策略数: {len(data.get('results', {}))}")
            print(f"  - 格式化消息长度: {len(data.get('formatted_message', ''))}")
        else:
            print(f"  - 错误响应: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False

def test_toggle_task():
    """测试切换定时任务状态"""
    try:
        payload = {"enabled": True}
        response = requests.post(
            f"{BASE_URL}/api/v1/multi-strategy/toggle-task",
            json=payload
        )
        print(f"✓ 切换定时任务 - 状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  - 执行状态: {'成功' if data.get('success') else '失败'}")
            print(f"  - 消息: {data.get('message')}")
        else:
            print(f"  - 错误响应: {response.text}")
        
        # 再次调用以关闭任务
        payload = {"enabled": False}
        response = requests.post(
            f"{BASE_URL}/api/v1/multi-strategy/toggle-task",
            json=payload
        )
        print(f"✓ 关闭定时任务 - 状态码: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("开始测试多策略筛选功能...")
    print("="*60)
    
    tests = [
        ("功能信息接口", test_multi_strategy_info),
        ("获取策略列表", test_get_strategies),
        ("手动执行策略", test_manual_execution),
        ("切换定时任务", test_toggle_task),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*60)
    print("测试汇总:")
    passed = 0
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总结果: {passed}/{len(results)} 项测试通过")
    return passed == len(results)

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)