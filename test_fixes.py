#!/usr/bin/env python3
"""
测试修复：健康检查API和100qiu数据获取功能
"""
import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

def test_health_check(source_id=1):
    """测试健康检查API"""
    print(f"\n=== 测试健康检查API (source_id={source_id}) ===")
    url = f"{BASE_URL}{API_PREFIX}/admin/sources/{source_id}/health"
    print(f"请求URL: {url}")
    
    # 前端使用POST方法
    try:
        response = requests.post(url, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {response.headers}")
        print(f"响应体: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("解析的JSON响应:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            if data.get("success"):
                print("✓ 健康检查API成功")
                return True
            else:
                print("✗ 健康检查API返回success=False")
                return False
        else:
            print(f"✗ 健康检查API返回非200状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 健康检查API请求异常: {e}")
        return False

def test_fetch_100qiu(source_id=1):
    """测试100qiu数据获取API"""
    print(f"\n=== 测试100qiu数据获取API (source_id={source_id}) ===")
    url = f"{BASE_URL}{API_PREFIX}/data-source-100qiu/{source_id}/fetch"
    print(f"请求URL: {url}")
    
    try:
        response = requests.post(url, timeout=30)
        print(f"状态码: {response.status_code}")
        print(f"响应体: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("解析的JSON响应:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            if data.get("success"):
                print("✓ 数据获取API成功")
                return True
            else:
                print("✗ 数据获取API返回success=False")
                return False
        else:
            print(f"✗ 数据获取API返回非200状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 数据获取API请求异常: {e}")
        return False

def main():
    print("开始测试修复...")
    
    # 测试健康检查
    health_ok = test_health_check(1)
    
    # 测试数据获取（需要确保source_id=1是100qiu数据源）
    fetch_ok = test_fetch_100qiu(1)
    
    print("\n=== 测试结果 ===")
    print(f"健康检查: {'通过' if health_ok else '失败'}")
    print(f"数据获取: {'通过' if fetch_ok else '失败'}")
    
    if health_ok and fetch_ok:
        print("✓ 所有测试通过！")
        return 0
    else:
        print("✗ 部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())