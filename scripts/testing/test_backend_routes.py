import urllib.request
import urllib.error
import json

def test_api_endpoint(url, method="GET"):
    """测试API端点"""
    try:
        req = urllib.request.Request(url, method=method)
        with urllib.request.urlopen(req, timeout=5) as response:
            result = response.read().decode('utf-8')
            return response.getcode(), result
    except urllib.error.HTTPError as e:
        try:
            error_body = e.read().decode('utf-8')
            return e.code, error_body
        except:
            return e.code, str(e)
    except Exception as e:
        return 0, f"Error: {str(e)}"

def main():
    base_url = "http://localhost:8000"
    
    print("测试后端API路由...")
    print("="*50)
    
    # 测试根路径
    status, result = test_api_endpoint(f"{base_url}/")
    print(f"根路径 (/): {status}")
    
    # 测试任务列表API
    status, result = test_api_endpoint(f"{base_url}/api/v1/admin/tasks?page=1&size=5")
    print(f"任务列表 (/api/v1/admin/tasks): {status}")
    
    # 测试任务统计API
    status, result = test_api_endpoint(f"{base_url}/api/v1/admin/tasks/statistics")
    print(f"任务统计 (/api/v1/admin/tasks/statistics): {status}")
    
    # 测试数据源API
    status, result = test_api_endpoint(f"{base_url}/api/v1/admin/data-sources?page=1&size=5")
    print(f"数据源列表 (/api/v1/admin/data-sources): {status}")
    
    # 测试请求头API
    status, result = test_api_endpoint(f"{base_url}/api/v1/admin/headers?page=1&size=5")
    print(f"请求头列表 (/api/v1/admin/headers): {status}")
    
    # 测试IP池API
    status, result = test_api_endpoint(f"{base_url}/api/v1/admin/ip-pools?page=1&size=5")
    print(f"IP池列表 (/api/v1/admin/ip-pools): {status}")
    
    print("="*50)
    print("API路由测试完成!")

if __name__ == "__main__":
    main()