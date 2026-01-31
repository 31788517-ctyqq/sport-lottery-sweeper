"""
日志管理模块测试脚本
用于测试日志API端点是否正常工作
"""
import requests
import json

# 测试后端API是否运行
BASE_URL = "http://localhost:8001"

def test_logs_api():
    """测试日志API端点"""
    print("测试日志管理API端点...")
    
    # 尝试获取系统日志
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/system/logs/db/system")
        print(f"系统日志API状态: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"系统日志数量: {len(data) if isinstance(data, list) else 'N/A'}")
        else:
            print(f"错误信息: {response.text}")
    except Exception as e:
        print(f"请求系统日志API时出错: {e}")

    # 尝试获取用户日志
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/system/logs/db/user")
        print(f"用户日志API状态: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"用户日志数量: {len(data) if isinstance(data, list) else 'N/A'}")
        else:
            print(f"错误信息: {response.text}")
    except Exception as e:
        print(f"请求用户日志API时出错: {e}")

    # 尝试获取安全日志
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/system/logs/db/security")
        print(f"安全日志API状态: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"安全日志数量: {len(data) if isinstance(data, list) else 'N/A'}")
        else:
            print(f"错误信息: {response.text}")
    except Exception as e:
        print(f"请求安全日志API时出错: {e}")

    # 尝试获取API日志
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/system/logs/db/api")
        print(f"API日志API状态: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"API日志数量: {len(data) if isinstance(data, list) else 'N/A'}")
        else:
            print(f"错误信息: {response.text}")
    except Exception as e:
        print(f"请求API日志API时出错: {e}")

if __name__ == "__main__":
    test_logs_api()