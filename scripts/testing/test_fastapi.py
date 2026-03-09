import asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
import sys
import traceback
from backend.main import app

def test_with_testclient():
    """使用TestClient测试FastAPI应用"""
    client = TestClient(app)
    
    # 测试获取用户列表
    print("测试获取用户列表...")
    try:
        response = client.get("/api/v1/admin/admin-users?skip=0&limit=10", headers={
            "Authorization": "Bearer dummy_token"
        })
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:500]}")
    except Exception as e:
        print(f"请求失败: {e}")
        traceback.print_exc()

    # 测试获取当前用户
    print("\n测试获取当前用户...")
    try:
        response = client.get("/api/v1/admin/admin-users/current-user", headers={
            "Authorization": "Bearer dummy_token"
        })
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:500]}")
    except Exception as e:
        print(f"请求失败: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_with_testclient()