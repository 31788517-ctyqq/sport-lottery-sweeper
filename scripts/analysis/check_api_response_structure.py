"""
检查API响应结构
"""
import urllib.request
import urllib.error
import json

BASE_URL = "http://localhost:8000"

def get_api_response(url):
    """获取API响应"""
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode('utf-8')
            return response.getcode(), json.loads(result)
    except urllib.error.HTTPError as e:
        try:
            error_body = e.read().decode('utf-8')
            return e.code, json.loads(error_body)
        except:
            return e.code, str(e)
    except Exception as e:
        return 0, f"Error: {str(e)}"

def main():
    print("检查API响应结构...")
    
    # 检查IP池管理API响应结构
    print("\n1. IP池管理API响应结构:")
    print("-" * 40)
    status, response = get_api_response(f"{BASE_URL}/api/v1/admin/ip-pools?page=1&size=10")
    print(f"状态码: {status}")
    print(f"响应内容: {json.dumps(response, indent=2, ensure_ascii=False)}")
    
    # 检查爬虫监控API响应结构
    print("\n2. 爬虫监控API响应结构:")
    print("-" * 40)
    status, response = get_api_response(f"{BASE_URL}/api/v1/admin/crawler/monitor/health")
    print(f"状态码: {status}")
    print(f"响应内容: {json.dumps(response, indent=2, ensure_ascii=False)}")
    
    # 检查任务管理API响应结构
    print("\n3. 任务管理API响应结构:")
    print("-" * 40)
    status, response = get_api_response(f"{BASE_URL}/api/v1/admin/tasks?page=1&size=10")
    print(f"状态码: {status}")
    print(f"响应内容: {json.dumps(response, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    main()