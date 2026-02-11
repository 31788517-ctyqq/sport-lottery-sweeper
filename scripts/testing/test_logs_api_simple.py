#!/usr/bin/env python3
"""
简单测试日志API端点
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查端点"""
    response = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
    print(f"健康检查: {response.status_code}")
    if response.status_code == 200:
        print(f"响应: {response.json()}")
    return response.status_code == 200

def test_system_logs_with_token(token):
    """使用令牌测试系统日志端点"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/admin/system/logs/db/system",
        params={"skip": 0, "limit": 5},
        headers=headers,
        timeout=5
    )
    print(f"系统日志API: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"返回 {len(data.get('items', []))} 条日志")
        print(f"总日志数: {data.get('total', 0)}")
        return True
    else:
        print(f"错误: {response.text}")
        return False

def main():
    """主函数"""
    print("开始测试日志API端点...")
    
    # 首先测试健康端点
    if not test_health():
        print("健康检查失败，后端可能未运行")
        return
    
    # 尝试从环境变量获取令牌，或使用硬编码令牌（仅用于测试）
    import os
    token = os.environ.get("ADMIN_TOKEN")
    if not token:
        # 尝试使用默认管理员凭据登录（假设存在）
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/admin/auth/login",
                json=login_data,
                timeout=5
            )
            if response.status_code == 200:
                token = response.json().get("access_token")
                print(f"登录成功，获取到令牌: {token[:20]}...")
            else:
                print(f"登录失败: {response.status_code}, {response.text}")
                token = None
        except Exception as e:
            print(f"登录异常: {e}")
            token = None
    
    if token:
        # 测试系统日志端点
        test_system_logs_with_token(token)
    else:
        print("无法获取管理员令牌，跳过认证测试")
        print("你可以设置ADMIN_TOKEN环境变量来测试认证端点")

if __name__ == "__main__":
    main()