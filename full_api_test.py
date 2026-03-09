#!/usr/bin/env python
"""
完整的API功能测试
验证用户管理页面API端点是否正常工作
"""

import requests
import json
from datetime import datetime, timedelta
import jwt
from backend.config import settings

# 生成一个有效的JWT令牌用于测试
def generate_test_token():
    """生成测试用的JWT令牌"""
    payload = {
        "user_id": 1,
        "username": "admin",
        "role": "admin",
        "user_type": "admin",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

def test_user_management_api():
    """测试用户管理API功能"""
    base_url = "http://localhost:8000/api/v1/admin"
    
    # 生成有效的测试令牌
    token = generate_test_token()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("开始测试用户管理API功能...")
    
    # 测试获取用户列表
    print("\n1. 测试获取用户列表...")
    try:
        response = requests.get(f"{base_url}/admin-users", headers=headers, params={
            "skip": 0,
            "limit": 10
        })
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   响应成功: {len(data.get('data', {}).get('items', []))} 个用户")
        else:
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"   请求失败: {e}")
    
    # 测试获取当前用户信息
    print("\n2. 测试获取当前用户信息...")
    try:
        response = requests.get(f"{base_url}/admin-users/current-user", headers=headers)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   响应成功: {data.get('data', {}).get('username', 'Unknown')} ")
        else:
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"   请求失败: {e}")
    
    # 测试获取用户统计信息
    print("\n3. 测试获取用户统计信息...")
    try:
        response = requests.get(f"{base_url}/admin-users/stats", headers=headers)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   响应成功: 统计信息获取成功")
        else:
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"   请求失败: {e}")
    
    # 测试获取概览统计
    print("\n4. 测试获取概览统计...")
    try:
        response = requests.get(f"{base_url}/admin-users/stats/overview", headers=headers)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   响应成功: 概览统计获取成功")
        else:
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"   请求失败: {e}")
    
    # 测试获取登录历史
    print("\n5. 测试获取登录历史...")
    try:
        response = requests.get(f"{base_url}/admin-users/login-history", headers=headers, params={
            "limit": 10
        })
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   响应成功: {len(data.get('data', []))} 条登录记录")
        else:
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"   请求失败: {e}")
    
    # 测试批量分配角色
    print("\n6. 测试批量分配角色...")
    try:
        response = requests.post(
            f"{base_url}/admin-users/batch-assign-roles",
            headers=headers,
            json={"userIds": [1], "roleIds": ["admin"]}
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   响应成功: {data.get('data', {}).get('message', 'Success')}")
        else:
            print(f"   错误信息: {response.text}")
    except Exception as e:
        print(f"   请求失败: {e}")
    
    print("\nAPI功能测试完成！")

if __name__ == "__main__":
    test_user_management_api()