"""
API认证测试脚本
用于验证API的认证功能是否正常工作
"""
import requests
import json

# 测试API端点
BASE_URL = "http://127.0.0.1:8000"

def test_unauthorized_access():
    """测试无认证访问"""
    print("测试无认证访问API...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/data-source-100qiu/")
        print(f"无认证访问状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"无认证访问失败: {e}")

def test_with_mock_token():
    """测试带假token的访问"""
    print("\n测试带假token的访问...")
    headers = {
        "Authorization": "Bearer fake-token",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(f"{BASE_URL}/api/v1/data-source-100qiu/", headers=headers)
        print(f"带假token访问状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"带假token访问失败: {e}")

def test_health_endpoint():
    """测试健康检查端点（应该是公开的）"""
    print("\n测试健康检查端点...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        print(f"健康检查状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"健康检查失败: {e}")

if __name__ == "__main__":
    print("开始API认证测试...")
    test_health_endpoint()
    test_unauthorized_access()
    test_with_mock_token()
    print("\nAPI认证测试完成")