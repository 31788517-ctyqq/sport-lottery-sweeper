"""
调试LLM端点可访问性
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """测试登录并返回令牌"""
    login_url = f"{BASE_URL}/api/v1/auth/login"
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"登录状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应结构: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 提取令牌
            if "data" in data and "access_token" in data["data"]:
                token = data["data"]["access_token"]
                print(f"提取的令牌: {token[:50]}...")
                return token
            else:
                print("无法找到access_token字段")
                return None
        else:
            print(f"登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"登录异常: {e}")
        return None

def test_endpoint(endpoint, token=None, method="GET", data=None):
    """测试单个端点"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json"
    
    print(f"\n测试端点: {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data or {})
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data or {})
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            print(f"不支持的方法: {method}")
            return False
        
        print(f"状态码: {response.status_code}")
        if response.status_code < 300:
            try:
                print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            except:
                print(f"响应文本: {response.text}")
            return True
        else:
            print(f"错误响应: {response.text}")
            return False
    except Exception as e:
        print(f"请求异常: {e}")
        return False

def main():
    print("=" * 60)
    print("调试LLM端点可访问性")
    print("=" * 60)
    
    # 1. 测试登录
    token = test_login()
    
    if not token:
        print("登录失败，无法继续测试需要认证的端点")
        return
    
    # 2. 测试不需要认证的端点（健康检查）
    print("\n" + "=" * 60)
    print("测试不需要认证的端点")
    print("=" * 60)
    
    test_endpoint("/api/v1/health", method="GET")
    
    # 3. 测试需要认证的端点
    print("\n" + "=" * 60)
    print("测试需要认证的LLM端点")
    print("=" * 60)
    
    endpoints = [
        ("/api/v1/llm-providers", "GET"),
        ("/api/v1/llm-providers/count", "GET"),
        ("/api/v1/llm-providers/stats/overview", "GET"),
        ("/api/v1/llm-providers/available/list", "GET"),
    ]
    
    for endpoint, method in endpoints:
        test_endpoint(endpoint, token, method)
    
    # 4. 测试数据库是否有现有供应商
    print("\n" + "=" * 60)
    print("检查现有供应商")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/v1/llm-providers", 
                           headers={"Authorization": f"Bearer {token}"})
    if response.status_code == 200:
        providers = response.json()
        print(f"现有供应商数量: {len(providers)}")
        for i, provider in enumerate(providers[:3]):  # 显示前3个
            print(f"  {i+1}. {provider.get('name')} - {provider.get('provider_type')}")
    else:
        print(f"获取供应商失败: {response.status_code}")

if __name__ == "__main__":
    main()