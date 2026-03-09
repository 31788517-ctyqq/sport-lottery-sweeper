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
    print("检查admin登录API...")
    
    # 测试正确的登录API路径
    print("\n1. 测试正确的登录API路径...")
    login_url = "http://localhost:8000/api/v1/admin/login"
    print(f"   测试: {login_url}")
    
    # 尝试POST请求（预期422 - 参数验证错误，而不是404）
    login_data = {"username": "admin", "password": "admin123"}
    resp = check_api_endpoint(login_url, method='POST', data=login_data)
    print(f"   POST请求状态: {resp['status']}")
    
    if resp['status'] == 422 or resp['status'] == 401:
        print("   ✓ 登录API存在（422/401状态码表明API存在但参数/认证有问题）")
    elif resp['status'] == 404:
        print("   ✗ 登录API不存在")
    elif resp['status'] == 405:
        print("   ✓ 登录API存在（405 Method Not Allowed - 说明GET方法不被允许）")
    else:
        print(f"   ? 登录API状态: {resp['status']}")
    
    # 测试用户API
    print("\n2. 测试用户API...")
    user_url = "http://localhost:8000/api/v1/admin/admin-users"
    resp = check_api_endpoint(user_url)
    print(f"   GET {user_url}: {resp['status']}")
    
    if resp['status'] in [200, 401, 403, 422]:
        print("   ✓ 用户API存在")
    elif resp['status'] == 404:
        print("   ✗ 用户API不存在")
    else:
        print(f"   ? 用户API状态: {resp['status']}")
    
    # 测试GET登录方法（应该返回405）
    print("\n3. 测试GET登录方法...")
    resp = check_api_endpoint(login_url, method='GET')
    print(f"   GET {login_url}: {resp['status']}")
    
    if resp['status'] == 405:
        print("   ✓ 登录API存在（405 Method Not Allowed）")
    else:
        print(f"   ? 登录API GET方法状态: {resp['status']}")

if __name__ == "__main__":
    main()