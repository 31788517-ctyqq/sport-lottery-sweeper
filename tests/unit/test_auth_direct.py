#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接测试auth login端点
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from fastapi.testclient import TestClient
from backend.main import app

def test_auth_login_direct():
    """直接测试auth login端点"""
    client = TestClient(app)
    
    print("测试 auth/login 端点...")
    response = client.post("/api/v1/auth/login", json={
        "username": "test",
        "password": "test"
    })
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    return response.status_code

if __name__ == "__main__":
    try:
        status_code = test_auth_login_direct()
        if status_code in [200, 401]:
            print("✓ 测试通过 - 返回了预期的状态码")
        else:
            print(f"✗ 测试失败 - 返回了意外的状态码: {status_code}")
    except Exception as e:
        print(f"✗ 测试异常: {e}")
        import traceback
        traceback.print_exc()