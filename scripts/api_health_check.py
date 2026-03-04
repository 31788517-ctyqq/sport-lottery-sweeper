#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API健康检查脚本
用于检查后端API端点的可用性和响应状态
"""

import os
import sys
import requests
import json
from pathlib import Path
from typing import Dict, List, Tuple
import time


def get_base_url():
    """获取基础URL"""
    # 从环境变量或默认值获取
    base_url = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
    return base_url


def check_api_health(base_url: str) -> bool:
    """检查API健康状态"""
    health_url = f"{base_url}/health"
    try:
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            print(f"✅ API健康检查通过: {health_url}, 状态码: {response.status_code}")
            try:
                data = response.json()
                print(f"   响应内容: {data}")
            except:
                print(f"   响应内容: {response.text[:100]}...")
            return True
        else:
            print(f"❌ API健康检查失败: {health_url}, 状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API健康检查异常: {health_url}, 错误: {str(e)}")
        return False


def check_api_endpoints(base_url: str) -> List[Tuple[str, int, str]]:
    """检查主要API端点"""
    endpoints = [
        ("/api/v1/users/me", "GET"),
        ("/api/v1/admin/dashboard", "GET"),
        ("/api/v1/datasources", "GET"),
        ("/api/v1/tasks", "GET"),
        ("/api/v1/logs", "GET"),
    ]
    
    results = []
    
    for endpoint, method in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, timeout=10, json={})
            else:
                continue
                
            status = response.status_code
            if status == 200 or status == 401 or status == 405:  # 401是认证错误，405是方法不允许，都是正常的
                status_text = "正常"
            elif status >= 500:
                status_text = "服务器错误"
            elif status >= 400:
                status_text = "客户端错误"
            else:
                status_text = "未知"
                
            results.append((url, status, status_text))
            print(f"   {method} {endpoint}: {status} ({status_text})")
        except requests.exceptions.RequestException as e:
            results.append((url, -1, f"请求错误: {str(e)}"))
            print(f"   {method} {endpoint}: 请求错误 ({str(e)})")
    
    return results


def check_authentication(base_url: str) -> bool:
    """检查认证端点"""
    auth_url = f"{base_url}/api/auth/login"
    
    # 尝试使用默认管理员凭据登录
    default_credentials = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(auth_url, json=default_credentials, timeout=10)
        if response.status_code in [200, 401]:  # 200是成功，401是认证失败，都是正常响应
            print(f"✅ 认证端点检查通过: {auth_url}, 状态码: {response.status_code}")
            return True
        else:
            print(f"⚠️  认证端点异常: {auth_url}, 状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 认证端点异常: {auth_url}, 错误: {str(e)}")
        return False


def run_api_health_checks():
    """运行API健康检查"""
    print("=" * 60)
    print("API健康检查")
    print("=" * 60)
    
    base_url = get_base_url()
    print(f"检查目标: {base_url}")
    
    # 检查API健康状态
    print("\n🔍 检查API健康状态...")
    health_ok = check_api_health(base_url)
    
    # 检查认证端点
    print("\n🔍 检查认证端点...")
    auth_ok = check_authentication(base_url)
    
    # 检查主要API端点
    print("\n🔍 检查主要API端点...")
    endpoint_results = check_api_endpoints(base_url)
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("API健康检查结果:")
    print("=" * 60)
    
    print(f"健康检查: {'✅ 通过' if health_ok else '❌ 失败'}")
    print(f"认证检查: {'✅ 通过' if auth_ok else '❌ 失败'}")
    
    if endpoint_results:
        print("\nAPI端点详情:")
        for url, status, status_text in endpoint_results:
            if status == -1:
                status_str = "❌ 请求错误"
            elif status < 400:
                status_str = f"✅ 正常 ({status})"
            elif status < 500:
                status_str = f"⚠️  客户端错误 ({status})"
            else:
                status_str = f"❌ 服务器错误 ({status})"
            print(f"  {status_str}: {url.split('/')[-1]}")
    
    overall_success = health_ok and auth_ok
    print(f"\n总体评估: {'✅ API服务正常' if overall_success else '❌ API服务存在问题'}")
    
    return overall_success


def run_detailed_error_check(base_url: str):
    """运行详细的错误检查"""
    print("\n🔍 运行详细错误检查...")
    
    # 检查常见的422和500错误
    problematic_endpoints = [
        "/api/v1/admin/crawler/headers/{header_id}",  # 这些是已知的422错误端点
        "/api/v1/admin/datasources/{source_id}",
        "/api/v1/admin/tasks/{task_id}",
        "/api/v1/admin/logs/{log_id}",
    ]
    
    # 替换路径参数为测试ID
    actual_endpoints = [
        ep.replace("{header_id}", "1").replace("{source_id}", "1").replace("{task_id}", "1").replace("{log_id}", "1")
        for ep in problematic_endpoints
    ]
    
    for endpoint in actual_endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 422:
                print(f"   ⚠️  422错误: {endpoint}")
            elif response.status_code >= 500:
                print(f"   ❌ 500错误: {endpoint}")
            elif response.status_code in [200, 401, 404, 405]:
                print(f"   ✅ 正常响应: {endpoint} ({response.status_code})")
            else:
                print(f"   ?  其他状态: {endpoint} ({response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ 请求异常: {endpoint} ({str(e)})")


if __name__ == "__main__":
    success = run_api_health_checks()
    
    base_url = get_base_url()
    run_detailed_error_check(base_url)
    
    sys.exit(0 if success else 1)