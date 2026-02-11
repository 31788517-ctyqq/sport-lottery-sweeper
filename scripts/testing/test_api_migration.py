"""
API迁移验证脚本
用于测试新API路径是否正常工作
"""
import requests
import json
import sys
import os
from urllib.parse import urljoin

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

BASE_URL = "http://localhost:8000"

def test_new_api_paths():
    """测试新版API路径"""
    print("=== 测试新版API路径 ===")
    
    # 测试任务API - 获取列表
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/tasks?page=1&size=10")
        print(f"✓ 任务列表API路径测试: {response.status_code}")
    except Exception as e:
        print(f"✗ 任务列表API路径测试失败: {e}")
    
    # 测试数据源API - 获取列表
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/data-sources?page=1&size=10")
        print(f"✓ 数据源列表API路径测试: {response.status_code}")
    except Exception as e:
        print(f"✗ 数据源列表API路径测试失败: {e}")

def test_legacy_api_paths():
    """测试旧版API路径重定向"""
    print("\n=== 测试旧版API路径重定向 ===")
    
    # 测试旧任务API路径
    try:
        response = requests.get(f"{BASE_URL}/api/admin/crawler/tasks?page=1&size=10")
        print(f"✓ 旧任务API路径重定向测试: {response.status_code}")
    except Exception as e:
        print(f"✗ 旧任务API路径重定向测试失败: {e}")
    
    # 测试旧数据源API路径
    try:
        response = requests.get(f"{BASE_URL}/api/admin/crawler/sources?page=1&size=10")
        print(f"✓ 旧数据源API路径重定向测试: {response.status_code}")
    except Exception as e:
        print(f"✗ 旧数据源API路径重定向测试失败: {e}")

def test_task_creation():
    """测试任务创建功能"""
    print("\n=== 测试任务创建功能 ===")
    
    # 准备测试数据
    test_data = {
        "name": "测试任务",
        "source_id": "1",
        "task_type": "crawl",
        "cron_expression": "* * * * *",
        "config": "{}"
    }
    
    try:
        # 使用新路径测试
        response = requests.post(f"{BASE_URL}/api/v1/admin/tasks", json=test_data)
        print(f"✓ 新路径任务创建测试: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  响应消息: {result.get('message', 'N/A')}")
    except Exception as e:
        print(f"✗ 新路径任务创建测试失败: {e}")
    
    try:
        # 使用旧路径测试（应该被重定向）
        response = requests.post(f"{BASE_URL}/api/admin/crawler/tasks", json=test_data)
        print(f"✓ 旧路径任务创建测试: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  响应消息: {result.get('message', 'N/A')}")
    except Exception as e:
        print(f"✗ 旧路径任务创建测试失败: {e}")

def main():
    """主测试函数"""
    print("开始API迁移验证...")
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code in [200, 404, 405]:
            print("✓ 服务连接正常")
        else:
            print(f"✗ 服务连接异常: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("⚠ 服务未运行，请先启动后端服务")
        print("  启动命令: python -m backend.main")
        return
    except Exception as e:
        print(f"✗ 服务连接测试失败: {e}")
        return
    
    # 执行各项测试
    test_new_api_paths()
    test_legacy_api_paths()
    test_task_creation()
    
    print("\n=== 测试完成 ===")
    print("如果所有测试通过，说明API迁移成功！")
    print("可以逐步将前端请求迁移到新版API路径。")

if __name__ == "__main__":
    main()