#!/usr/bin/env python3
"""
测试修复：健康检查API和100qiu数据获取功能（简单版）
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

def test_health_check_get(source_id=1):
    """测试健康检查API GET方法"""
    print(f"\n=== 测试健康检查API GET (source_id={source_id}) ===")
    url = f"{BASE_URL}{API_PREFIX}/admin/sources/{source_id}/health"
    print(f"请求URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应体: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("解析的JSON响应:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            if data.get("success"):
                print("PASS: 健康检查API GET成功")
                return True
            else:
                print("FAIL: 健康检查API GET返回success=False")
                return False
        else:
            print(f"FAIL: 健康检查API GET返回非200状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: 健康检查API GET请求异常: {e}")
        return False

def test_health_check_post(source_id=1):
    """测试健康检查API POST方法"""
    print(f"\n=== 测试健康检查API POST (source_id={source_id}) ===")
    url = f"{BASE_URL}{API_PREFIX}/admin/sources/{source_id}/health"
    print(f"请求URL: {url}")
    
    try:
        response = requests.post(url, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应头中的Allow字段: {response.headers.get('allow', 'N/A')}")
        print(f"响应体: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("解析的JSON响应:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            if data.get("success"):
                print("PASS: 健康检查API POST成功")
                return True
            else:
                print("FAIL: 健康检查API POST返回success=False")
                return False
        else:
            print(f"FAIL: 健康检查API POST返回非200状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: 健康检查API POST请求异常: {e}")
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
                print("PASS: 数据获取API成功")
                return True
            else:
                print("FAIL: 数据获取API返回success=False")
                return False
        else:
            print(f"FAIL: 数据获取API返回非200状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: 数据获取API请求异常: {e}")
        return False

def main():
    print("开始测试修复...")
    
    # 测试健康检查GET
    health_get_ok = test_health_check_get(1)
    
    # 测试健康检查POST
    health_post_ok = test_health_check_post(1)
    
    # 测试数据获取（需要确保source_id=1是100qiu数据源）
    fetch_ok = test_fetch_100qiu(1)
    
    print("\n=== 测试结果 ===")
    print(f"健康检查GET: {'PASS' if health_get_ok else 'FAIL'}")
    print(f"健康检查POST: {'PASS' if health_post_ok else 'FAIL'}")
    print(f"数据获取: {'PASS' if fetch_ok else 'FAIL'}")
    
    if health_get_ok and health_post_ok and fetch_ok:
        print("所有测试通过！")
        return 0
    else:
        print("部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())