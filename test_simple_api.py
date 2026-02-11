#!/usr/bin/env python3
"""
简单API测试脚本
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("1. 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text[:100]}")
        return response.status_code == 200
    except Exception as e:
        print(f"   错误: {e}")
        return False

def test_auth_login():
    """测试认证登录"""
    print("\n2. 测试管理员登录...")
    
    # 尝试几个可能的用户名/密码组合
    test_credentials = [
        {"username": "admin", "password": "admin123"},
        {"username": "admin", "password": "password"},
        {"username": "administrator", "password": "admin123"},
        {"username": "superadmin", "password": "admin123"},
    ]
    
    for creds in test_credentials:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/login",
                json=creds,
                timeout=5
            )
            print(f"   尝试 {creds['username']}/{creds['password']}: 状态码 {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   成功! 响应: {json.dumps(data, ensure_ascii=False)[:150]}")
                return True, data.get("data", {}).get("access_token")
        except Exception as e:
            print(f"   请求异常: {e}")
    
    return False, None

def test_data_sources():
    """测试数据源API"""
    print("\n3. 测试数据源API...")
    
    # 尝试不同端点
    endpoints = [
        "/api/v1/admin/sources",
        "/api/v1/data-sources",
        "/api/v1/crawler/sources",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            print(f"   {endpoint}: 状态码 {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   成功! 数据: {json.dumps(data, ensure_ascii=False)[:200]}")
                    return True, endpoint
                except:
                    print(f"   响应内容: {response.text[:200]}")
        except Exception as e:
            print(f"   请求异常: {e}")
    
    return False, None

def test_tasks():
    """测试任务API"""
    print("\n4. 测试任务API...")
    
    # 尝试不同端点
    endpoints = [
        "/api/v1/admin/tasks",
        "/api/v1/crawler/tasks",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            print(f"   {endpoint}: 状态码 {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   成功! 数据: {json.dumps(data, ensure_ascii=False)[:200]}")
                    return True, endpoint
                except:
                    print(f"   响应内容: {response.text[:200]}")
        except Exception as e:
            print(f"   请求异常: {e}")
    
    return False, None

def main():
    print(f"API测试开始 - 后端地址: {BASE_URL}")
    print("="*60)
    
    # 测试健康检查
    if not test_health():
        print("\n❌ 健康检查失败，后端服务可能未运行")
        sys.exit(1)
    
    # 测试登录
    login_success, token = test_auth_login()
    if not login_success:
        print("\n⚠️  管理员登录失败，可能没有合适的账户")
        print("   继续测试匿名API...")
        token = None
    
    # 测试数据源API
    ds_success, ds_endpoint = test_data_sources()
    
    # 测试任务API  
    task_success, task_endpoint = test_tasks()
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总:")
    print(f"   健康检查: {'✅ 通过' if test_health() else '❌ 失败'}")
    print(f"   管理员登录: {'✅ 成功' if login_success else '⚠️  失败'}")
    print(f"   数据源API: {'✅ 可访问' if ds_success else '❌ 不可访问'} ({ds_endpoint or '无'})")
    print(f"   任务API: {'✅ 可访问' if task_success else '❌ 不可访问'} ({task_endpoint or '无'})")
    
    if ds_success and task_success:
        print("\n✅ API测试基本通过，可以尝试创建数据源和任务")
        return True
    else:
        print("\n❌ API测试失败，需要检查后端服务配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)