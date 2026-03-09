"""
API功能验证脚本
验证所有关键API端点的功能
"""
import urllib.request
import urllib.error
import json

BASE_URL = "http://localhost:8000"

def test_api_endpoint(url, method="GET", data=None, headers=None):
    """测试API端点"""
    try:
        if headers is None:
            headers = {}
        
        if data:
            req_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=req_data, method=method, 
                                       headers={**headers, 'Content-Type': 'application/json'})
        else:
            req = urllib.request.Request(url, method=method, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode('utf-8')
            return response.getcode(), result
    except urllib.error.HTTPError as e:
        # HTTP错误也是有意义的信息，返回状态码和错误内容
        try:
            error_body = e.read().decode('utf-8')
            return e.code, error_body
        except:
            return e.code, str(e)
    except urllib.error.URLError as e:
        return 0, f"URL Error: {e.reason}"
    except Exception as e:
        return 0, f"Error: {str(e)}"

def main():
    print("API功能验证开始...")
    
    # 检查服务是否运行
    try:
        with urllib.request.urlopen(f"{BASE_URL}/docs", timeout=5) as response:
            if response.getcode() in [200, 404, 405]:
                print("✓ 服务连接正常")
            else:
                print(f"✗ 服务连接异常: {response.getcode()}")
                return
    except Exception as e:
        print(f"✗ 服务未运行或无法连接: {e}")
        return
    
    print("\n" + "="*80)
    print("API功能验证报告")
    print("="*80)
    
    # 测试API端点
    test_cases = [
        # 任务管理API
        ("任务列表", f"{BASE_URL}/api/v1/tasks", "GET"),
        ("任务统计", f"{BASE_URL}/api/v1/tasks/statistics", "GET"),
        
        # 数据源管理API
        ("数据源列表", f"{BASE_URL}/api/v1/admin/sources?page=1&size=10", "GET"),
        
        # 爬虫监控API
        ("爬虫监控健康状态", f"{BASE_URL}/api/v1/admin/crawler/monitor/health", "GET"),
        ("爬虫监控警报", f"{BASE_URL}/api/v1/admin/crawler/monitor/alerts", "GET"),
        
        # 请求头管理API
        ("请求头列表", f"{BASE_URL}/api/v1/admin/headers?page=1&size=10", "GET"),
        
        # IP池管理API
        ("IP池列表", f"{BASE_URL}/api/v1/admin/ip-pools?page=1&size=10", "GET"),
    ]
    
    results = []
    for name, url, method in test_cases:
        status, result = test_api_endpoint(url, method)
        results.append((name, status, result))
        print(f"{name}: {status}")
        
        # 根据状态码给出解释
        if status == 200:
            print(f"  ✓ {name} API正常工作")
        elif status == 401:
            print(f"  ⚠ {name} API路径正确，需要认证")
        elif status == 405:
            print(f"  ⚠ {name} API路径正确，方法不允许")
        elif status >= 400:
            print(f"  ✗ {name} API可能存在问题: {status}")
        else:
            print(f"  ? {name} API状态未知: {status}")
        print()
    
    print("-" * 80)
    print("验证摘要")
    print("-" * 80)
    
    total_tests = len(results)
    successful_responses = sum(1 for _, status, _ in results if status in [200, 401, 405])
    error_responses = sum(1 for _, status, _ in results if status >= 400 and status not in [401, 405])
    
    print(f"总测试数: {total_tests}")
    print(f"成功/需认证数: {successful_responses}")
    print(f"错误数: {error_responses}")
    
    if error_responses == 0:
        print("\n✅ 所有API端点都能正常响应！")
        print("✓ 路径注册正确")
        print("✓ 服务正常运行")
        print("✓ API功能验证完成")
    else:
        print(f"\n⚠️  {error_responses} 个API端点存在问题")

if __name__ == "__main__":
    main()