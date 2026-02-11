"""
验证新添加的IP池和请求头管理API端点
"""
import requests
import json

def verify_endpoints():
    base_url = "http://localhost:8000"
    
    print("="*60)
    print("验证新API端点")
    print("="*60)
    
    # 测试IP池管理API端点
    print("\n--- 测试IP池管理API端点 ---")
    ip_pool_endpoints = [
        ("/api/v1/admin/ip-pools", "GET"),
        ("/api/v1/admin/ip-pools", "POST"),
    ]
    
    for endpoint, method in ip_pool_endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}")
            elif method == "POST":
                response = requests.post(f"{base_url}{endpoint}", json={})
            elif method == "PUT":
                response = requests.put(f"{base_url}{endpoint}", json={})
            elif method == "DELETE":
                response = requests.delete(f"{base_url}{endpoint}")
            
            print(f"{method} {endpoint}: {response.status_code} - {'✅ 存在' if response.status_code != 404 else '❌ 不存在'}")
        except Exception as e:
            print(f"{method} {endpoint}: ❌ 请求失败 - {str(e)}")
    
    # 测试请求头管理API端点
    print("\n--- 测试请求头管理API端点 ---")
    header_endpoints = [
        ("/api/v1/admin/headers", "GET"),
        ("/api/v1/admin/headers", "POST"),
    ]
    
    for endpoint, method in header_endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}")
            elif method == "POST":
                response = requests.post(f"{base_url}{endpoint}", json={})
            elif method == "PUT":
                response = requests.put(f"{base_url}{endpoint}", json={})
            elif method == "DELETE":
                response = requests.delete(f"{base_url}{endpoint}")
            
            print(f"{method} {endpoint}: {response.status_code} - {'✅ 存在' if response.status_code != 404 else '❌ 不存在'}")
        except Exception as e:
            print(f"{method} {endpoint}: ❌ 请求失败 - {str(e)}")
    
    print("\n" + "="*60)
    print("验证完成")
    print("="*60)

if __name__ == "__main__":
    verify_endpoints()