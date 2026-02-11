#!/usr/bin/env python3
"""
简单测试LLM供应商端点
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_endpoint(endpoint):
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, timeout=5)
        print(f"测试 {url}:")
        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"  响应: {response.json()}")
        else:
            print(f"  错误: {response.text}")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"测试 {url}:")
        print(f"  异常: {e}")
        print()
        return False

print("测试LLM供应商端点...")
print("=" * 50)

endpoints = [
    "/llm-providers",
    "/llm-providers/count", 
    "/llm-providers/stats/overview",
    "/llm-providers/available/list"
]

results = []
for endpoint in endpoints:
    success = test_endpoint(endpoint)
    results.append((endpoint, success))

print("测试结果:")
print("=" * 50)
for endpoint, success in results:
    status = "通过" if success else "失败"
    print(f"{endpoint}: {status}")

total = len(results)
passed = sum(1 for _, success in results if success)
print(f"\n总计: {passed}/{total} 通过")