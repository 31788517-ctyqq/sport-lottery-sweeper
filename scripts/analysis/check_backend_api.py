import urllib.request
import urllib.error
from urllib.parse import urlencode
import json
import ssl

# 禁用SSL证书验证
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def check_api_endpoint(url, method='GET', headers=None, data=None):
    """检查API端点状态"""
    try:
        if data and method != 'GET':
            if isinstance(data, dict):
                data = json.dumps(data).encode('utf-8')
                if headers is None:
                    headers = {}
                headers['Content-Type'] = 'application/json'
        
        req = urllib.request.Request(url, method=method, data=data)
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)
        
        response = urllib.request.urlopen(req, context=ssl_context)
        return {
            'status': response.getcode(),
            'headers': dict(response.headers),
            'response': response.read().decode('utf-8')
        }
    except urllib.error.HTTPError as e:
        return {
            'status': e.code,
            'headers': dict(e.headers),
            'response': e.read().decode('utf-8') if e.read() else 'No response body'
        }
    except urllib.error.URLError as e:
        return {
            'status': None,
            'error': str(e),
            'response': 'Could not connect to server'
        }

def main():
    print("检查后端API端点状态...")
    
    # 测试基本连接
    print("\n1. 测试基本连接...")
    health_resp = check_api_endpoint("http://localhost:8000/api/v1/health")
    print(f"   Health Check: {health_resp['status']}")
    
    # 检查API文档
    print("\n2. 检查API文档...")
    docs_resp = check_api_endpoint("http://localhost:8000/docs")
    print(f"   API Docs: {docs_resp['status']}")
    
    # 测试用户管理API
    print("\n3. 测试用户管理API...")
    user_endpoints = [
        "http://localhost:8000/api/v1/admin/admin-users",
        "http://localhost:8000/api/v1/admin/users", 
        "http://localhost:8000/api/v1/admin/login"
    ]
    
    for endpoint in user_endpoints:
        resp = check_api_endpoint(endpoint)
        print(f"   {endpoint}: {resp['status']}")
        
        # 如果是登录API，尝试获取一些信息
        if 'login' in endpoint and resp['status'] == 405:  # 405表示端点存在但方法不对
            print(f"     ✓ 端点存在 (405 Method Not Allowed is expected for GET on login)")
        elif resp['status'] == 404:
            print(f"     ✗ 端点不存在")
        elif resp['status'] in [200, 401, 403, 422]:
            print(f"     ✓ 端点存在")
    
    # 测试admin相关API
    print("\n4. 测试admin相关API...")
    admin_endpoints = [
        "http://localhost:8000/api/v1/admin/data-sources",
        "http://localhost:8000/api/v1/admin/tasks",
        "http://localhost:8000/api/v1/admin/headers",
        "http://localhost:8000/api/v1/admin/ip-pools"
    ]
    
    for endpoint in admin_endpoints:
        resp = check_api_endpoint(endpoint)
        print(f"   {endpoint}: {resp['status']}")
        if resp['status'] in [200, 401, 403, 422]:
            print(f"     ✓ 端点存在")
        elif resp['status'] == 404:
            print(f"     ✗ 端点不存在")

if __name__ == "__main__":
    main()