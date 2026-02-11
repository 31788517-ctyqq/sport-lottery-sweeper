"""
检查API端点是否存在的简单脚本
"""
import requests
import sys

def check_endpoint(base_url, endpoint):
    """检查API端点"""
    try:
        url = f"{base_url}{endpoint}"
        response = requests.get(url, timeout=5)
        return response.status_code
    except Exception as e:
        print(f"访问 {endpoint} 失败: {str(e)}")
        return None

def main():
    base_url = "http://localhost:8000"
    
    print("检查数据源管理相关API端点...")
    
    # 根据main.py中的路由配置，数据源管理API应该在 /admin 前缀下
    endpoints_to_check = [
        "/api/v1/admin/sources",
        "/api/v1/admin/sources/1",
        "/api/v1/admin/sources/1/health",
        "/api/v1/admin/sources/1/test-connection",
        "/docs"
    ]
    
    for endpoint in endpoints_to_check:
        status = check_endpoint(base_url, endpoint)
        if status:
            print(f"{endpoint}: {status}")
        else:
            print(f"{endpoint}: 无法访问")
    
    print("API端点检查完成")

if __name__ == "__main__":
    main()