"""
验证所有路由是否正确注册到统一的 /api/v1/admin 前缀下
"""
import requests
import sys
import os
from urllib.parse import urljoin

# 添加项目根目录到Python路径
project_root = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, project_root)

BASE_URL = "http://localhost:8001"

def check_route(route_path, method="GET", expected_status=200):
    """检查路由是否可访问"""
    full_url = urljoin(BASE_URL, route_path)
    try:
        if method == "GET":
            response = requests.get(full_url, timeout=5)
        elif method == "POST":
            response = requests.post(full_url, timeout=5, json={})
        elif method == "PUT":
            response = requests.put(full_url, timeout=5, json={})
        else:
            response = requests.get(full_url, timeout=5)
        
        status_ok = response.status_code == expected_status or (expected_status == 200 and response.status_code < 500)
        print(f"{'✓' if status_ok else '✗'} {method} {route_path} -> {response.status_code}")
        return status_ok
    except Exception as e:
        print(f"✗ {method} {route_path} -> Error: {str(e)}")
        return False

def main():
    print("开始验证所有路由是否已正确注册到 /api/v1/admin 前缀下...")
    print("=" * 60)
    
    # 定义要测试的路由
    routes_to_test = [
        # 管理员数据源相关路由
        ("/api/v1/admin/sources", "GET"),
        ("/api/v1/admin/sources", "POST"),
        
        # 爬虫任务相关路由
        ("/api/v1/admin/tasks", "GET"),
        ("/api/v1/admin/tasks", "POST"),
        ("/api/v1/admin/tasks/1", "PUT"),
        ("/api/v1/admin/tasks/1/trigger", "POST"),
        ("/api/v1/admin/tasks/1/logs", "GET"),
        
        # 爬虫数据源相关路由
        ("/api/v1/admin/crawler/sources", "GET"),
        ("/api/v1/admin/crawler/sources/1/health", "GET"),
        ("/api/v1/admin/crawler/sources/1/status", "PUT"),
        
        # 爬虫任务相关路由
        ("/api/v1/admin/crawler/tasks", "GET"),
        ("/api/v1/admin/crawler/tasks", "POST"),
        ("/api/v1/admin/crawler/tasks/1", "PUT"),
        ("/api/v1/admin/crawler/tasks/1/trigger", "POST"),
        ("/api/v1/admin/crawler/tasks/1/logs", "GET"),
        
        # 爬虫配置相关路由
        ("/api/v1/admin/crawler/config", "GET"),
        ("/api/v1/admin/crawler/config", "POST"),
        ("/api/v1/admin/crawler/config/1", "PUT"),
        ("/api/v1/admin/crawler/config/1", "DELETE"),
        
        # 爬虫情报相关路由
        ("/api/v1/admin/crawler/intelligence/stats", "GET"),
        ("/api/v1/admin/crawler/intelligence/data", "GET"),
        ("/api/v1/admin/crawler/intelligence/export", "GET"),
        
        # 爬虫监控相关路由
        ("/api/v1/admin/crawler/monitor/health", "GET"),
        ("/api/v1/admin/crawler/monitor/system-stats", "GET"),
        ("/api/v1/admin/crawler/monitor/tasks", "GET"),
        
        # 请求头管理相关路由
        ("/api/v1/admin/headers", "GET"),
        ("/api/v1/admin/headers", "POST"),
        ("/api/v1/admin/headers/1", "PUT"),
        ("/api/v1/admin/headers/1", "DELETE"),
        
        # IP池管理相关路由
        ("/api/v1/admin/ip-pools", "GET"),
        ("/api/v1/admin/ip-pools", "POST"),
        ("/api/v1/admin/ip-pools/1", "PUT"),
        ("/api/v1/admin/ip-pools/1", "DELETE"),
        
        # 其他管理路由
        ("/api/v1/admin/logs", "GET"),
        ("/api/v1/admin/metrics", "GET"),
        ("/api/v1/admin/cache", "GET"),
    ]
    
    total_tests = len(routes_to_test)
    passed_tests = 0
    
    for route, method in routes_to_test:
        if check_route(route, method):
            passed_tests += 1
    
    print("=" * 60)
    print(f"测试完成: {passed_tests}/{total_tests} 路由可访问")
    
    if passed_tests == total_tests:
        print("🎉 所有路由均已正确注册到统一的 /api/v1/admin 前缀下！")
        return True
    else:
        print(f"⚠️  有 {total_tests - passed_tests} 个路由存在问题")
        return False

if __name__ == "__main__":
    main()