"""
测试所有关键API端点
"""
import requests

def test_all_endpoints():
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/api/v1/admin/sources",  # 数据源列表
        "/api/v1/crawler/tasks",  # 任务列表
        "/api/v1/crawler/tasks/statistics",  # 任务统计
        "/api/v1/health",  # 健康检查
    ]
    
    print("测试所有关键API端点:")
    print("="*60)
    
    for endpoint in endpoints:
        print(f"\n测试: {endpoint}")
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"  状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  响应: {str(data)[:100]}...")
            else:
                print(f"  错误: {response.text[:100]}...")
        except Exception as e:
            print(f"  请求错误: {e}")

if __name__ == "__main__":
    test_all_endpoints()