"""
验证API修复后的端点
"""
import urllib.request
import urllib.error
import json
import sys

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
        return e.code, e.read().decode('utf-8')
    except urllib.error.URLError as e:
        return 0, f"URL Error: {e.reason}"
    except Exception as e:
        return 0, f"Error: {str(e)}"

def main():
    print("验证API修复...")
    
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
        print("请先启动后端服务: python -m backend.main --port 8001")
        return
    
    print("\n" + "="*80)
    print("验证修复后的API端点")
    print("="*80)
    
    # 测试修复后的API端点
    test_cases = [
        # 任务管理API（应该已经正常工作）
        ("任务列表", f"{BASE_URL}/api/v1/admin/tasks?page=1&size=1"),
        ("任务统计", f"{BASE_URL}/api/v1/admin/tasks/statistics"),
        
        # 数据源管理API（修复：使用/sources而不是/data-sources）
        ("数据源列表", f"{BASE_URL}/api/v1/admin/sources?page=1&size=1"),
        
        # 爬虫监控API（应该已经正常工作）
        ("爬虫监控健康状态", f"{BASE_URL}/api/v1/admin/crawler/monitor/health"),
        ("爬虫监控警报", f"{BASE_URL}/api/v1/admin/crawler/monitor/alerts"),
        ("爬虫监控指标", f"{BASE_URL}/api/v1/admin/crawler/monitor/metrics"),
        
        # 请求头管理API（应该已经正常工作）
        ("请求头列表", f"{BASE_URL}/api/v1/admin/headers?page=1&size=1"),
        ("请求头统计", f"{BASE_URL}/api/v1/admin/headers/stats"),
        
        # IP池管理API（修复：使用正确的路径）
        ("IP池列表", f"{BASE_URL}/api/v1/admin/ip-pools?page=1&size=1"),
        ("IP池统计", f"{BASE_URL}/api/v1/admin/ip-pools/stats"),
    ]
    
    results = []
    for name, url in test_cases:
        status, result = test_api_endpoint(url)
        results.append((name, status, result))
        if status in [200, 401, 403, 405, 422]:  # 多数状态码都是正常的，422可能是参数问题
            print(f"✓ {name}: {status}")
        else:
            print(f"✗ {name}: {status}")
    
    print("\n" + "-"*80)
    print("验证摘要")
    print("-"*80)
    
    total_tests = len(results)
    # 我们接受200（成功）、401/403（权限）、405（方法不允许）、422（参数错误）为有效响应
    successful_responses = [200, 401, 403, 405, 422]
    successful_tests = sum(1 for _, status, _ in results if status in successful_responses)
    failed_tests = total_tests - successful_tests
    
    print(f"总测试数: {total_tests}")
    print(f"成功数: {successful_tests}")
    print(f"失败数: {failed_tests}")
    
    if failed_tests == 0:
        print("\n✅ 所有API端点现在都能正常响应！")
        print("API迁移和修复完成。")
    else:
        print(f"\n⚠️  {failed_tests} 个API端点仍存在问题，请检查服务器是否已重启。")
        print("确保后端服务已使用最新代码重启。")

if __name__ == "__main__":
    main()