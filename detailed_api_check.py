"""
详细API验证脚本，检查具体错误
"""
import urllib.request
import urllib.error
import json

BASE_URL = "http://localhost:8001"

def test_api_endpoint(url, method="GET", data=None):
    """测试API端点"""
    try:
        if data:
            req_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=req_data, method=method, 
                                       headers={'Content-Type': 'application/json'})
        else:
            req = urllib.request.Request(url, method=method)
        
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
    print("详细API验证...")
    
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
    print("详细API端点验证")
    print("="*80)
    
    # 测试API端点，不带分页参数先测试
    test_cases = [
        # 任务管理API - 不带分页参数
        ("任务列表（无参数）", f"{BASE_URL}/api/v1/tasks"),
        ("任务统计", f"{BASE_URL}/api/v1/tasks/statistics"),
        
        # 数据源管理API
        ("数据源列表（无参数）", f"{BASE_URL}/api/v1/admin/sources"),
        
        # 爬虫监控API
        ("爬虫监控健康状态", f"{BASE_URL}/api/v1/admin/crawler/monitor/health"),
        
        # 请求头管理API
        ("请求头列表（无参数）", f"{BASE_URL}/api/v1/admin/headers"),
        
        # IP池管理API
        ("IP池列表（无参数）", f"{BASE_URL}/api/v1/admin/ip-pools"),
    ]
    
    for name, url in test_cases:
        status, result = test_api_endpoint(url)
        print(f"{name}: {status}")
        if status >= 400:
            print(f"  错误详情: {result[:200]}...")  # 只显示前200个字符
    
    print("\n" + "="*80)
    print("使用分页参数测试")
    print("="*80)
    
    # 测试带分页参数的API
    paginated_test_cases = [
        ("任务列表（带分页）", f"{BASE_URL}/api/v1/tasks?page=1&size=10"),
        ("数据源列表（带分页）", f"{BASE_URL}/api/v1/admin/sources?page=1&size=10"),
        ("请求头列表（带分页）", f"{BASE_URL}/api/v1/admin/headers?page=1&size=10"),
        ("IP池列表（带分页）", f"{BASE_URL}/api/v1/admin/ip-pools?page=1&size=10"),
    ]
    
    for name, url in paginated_test_cases:
        status, result = test_api_endpoint(url)
        print(f"{name}: {status}")
        if status >= 400:
            print(f"  错误详情: {result[:200]}...")  # 只显示前200个字符

if __name__ == "__main__":
    main()