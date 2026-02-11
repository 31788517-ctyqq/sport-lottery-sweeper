"""
测试API端点是否正确注册和响应
"""
import requests

def test_api_endpoints():
    base_url = "http://localhost:8002"
    
    print("测试API端点...")
    
    # 测试管理任务API - GET请求
    try:
        response = requests.get(f"{base_url}/api/v1/admin/tasks?page=1&size=1", timeout=10)
        print(f"GET /api/v1/admin/tasks: {response.status_code}")
        if response.status_code == 200:
            print("  ✓ GET /api/v1/admin/tasks 返回成功")
        elif response.status_code == 422:
            print("  ✓ GET /api/v1/admin/tasks 存在，参数验证错误")
        else:
            print(f"  ✗ GET /api/v1/admin/tasks 错误: {response.status_code}")
    except Exception as e:
        print(f"  ✗ GET /api/v1/admin/tasks 连接失败: {e}")
    
    # 测试管理任务API - POST请求
    try:
        response = requests.post(f"{base_url}/api/v1/admin/tasks", json={
            "name": "Test Task",
            "source_id": "1",
            "task_type": "crawl",
            "cron_expression": "0 * * * *",
            "config": "{}"
        }, timeout=10)
        print(f"POST /api/v1/admin/tasks: {response.status_code}")
        if response.status_code == 200:
            print("  ✓ POST /api/v1/admin/tasks 返回成功")
        elif response.status_code == 422:
            print("  ✓ POST /api/v1/admin/tasks 存在，参数验证错误")
        elif response.status_code == 405:
            print("  ✗ POST /api/v1/admin/tasks 方法不允许 - 路由未注册或不支持POST")
        else:
            print(f"  ✗ POST /api/v1/admin/tasks 错误: {response.status_code}")
    except Exception as e:
        print(f"  ✗ POST /api/v1/admin/tasks 连接失败: {e}")

    # 测试统计API
    try:
        response = requests.get(f"{base_url}/api/v1/admin/tasks/statistics", timeout=10)
        print(f"GET /api/v1/admin/tasks/statistics: {response.status_code}")
        if response.status_code == 200:
            print("  ✓ GET /api/v1/admin/tasks/statistics 返回成功")
        elif response.status_code == 404:
            print("  ✗ GET /api/v1/admin/tasks/statistics 不存在")
        else:
            print(f"  ? GET /api/v1/admin/tasks/statistics: {response.status_code}")
    except Exception as e:
        print(f"  ✗ GET /api/v1/admin/tasks/statistics 连接失败: {e}")

    # 测试爬虫任务API - GET请求
    try:
        response = requests.get(f"{base_url}/api/v1/admin/crawler/tasks", timeout=10)
        print(f"GET /api/v1/admin/crawler/tasks: {response.status_code}")
        if response.status_code == 200:
            print("  ✓ GET /api/v1/admin/crawler/tasks 返回成功")
        elif response.status_code == 422:
            print("  ✓ GET /api/v1/admin/crawler/tasks 存在，参数验证错误")
        else:
            print(f"  ? GET /api/v1/admin/crawler/tasks: {response.status_code}")
    except Exception as e:
        print(f"  ✗ GET /api/v1/admin/crawler/tasks 连接失败: {e}")

    # 测试爬虫任务API - POST请求
    try:
        response = requests.post(f"{base_url}/api/v1/admin/crawler/tasks", json={
            "name": "Test Task",
            "source_id": 1,
            "cron_expr": "0 * * * *"
        }, timeout=10)
        print(f"POST /api/v1/admin/crawler/tasks: {response.status_code}")
        if response.status_code == 200:
            print("  ✓ POST /api/v1/admin/crawler/tasks 返回成功")
        elif response.status_code == 422:
            print("  ✓ POST /api/v1/admin/crawler/tasks 存在，参数验证错误")
        elif response.status_code == 405:
            print("  ✗ POST /api/v1/admin/crawler/tasks 方法不允许")
        else:
            print(f"  ? POST /api/v1/admin/crawler/tasks: {response.status_code}")
    except Exception as e:
        print(f"  ✗ POST /api/v1/admin/crawler/tasks 连接失败: {e}")
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=10)
        print(f"GET /api/v1/health: {response.status_code}")
        if response.status_code == 200:
            print("  ✓ GET /api/v1/health 返回成功")
        else:
            print(f"  ✗ GET /api/v1/health 错误: {response.status_code}")
    except Exception as e:
        print(f"  ✗ GET /api/v1/health 连接失败: {e}")

    print("\nAPI测试完成")

if __name__ == "__main__":
    test_api_endpoints()