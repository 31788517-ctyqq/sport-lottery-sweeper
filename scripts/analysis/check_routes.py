"""
检查FastAPI已注册的路由
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def get_openapi_spec():
    """获取OpenAPI规范"""
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"无法获取OpenAPI规范: {response.status_code}")
            return None
    except Exception as e:
        print(f"获取OpenAPI规范时出错: {e}")
        return None

def get_registered_routes():
    """获取已注册的路由"""
    try:
        # 尝试从docs获取
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("文档页面可访问")
        
        # 获取OpenAPI规范
        spec = get_openapi_spec()
        if spec:
            paths = spec.get("paths", {})
            print(f"\n总路由数: {len(paths)}")
            
            # 查找LLM相关路由
            llm_routes = []
            for path, methods in paths.items():
                if "llm" in path.lower():
                    llm_routes.append(path)
            
            print(f"\nLLM相关路由 ({len(llm_routes)}):")
            for route in sorted(llm_routes):
                print(f"  {route}")
            
            # 显示所有路由（前20个）
            print(f"\n所有路由（前20个）:")
            for i, path in enumerate(sorted(paths.keys())):
                if i >= 20:
                    print(f"  ... 还有 {len(paths) - 20} 个路由")
                    break
                print(f"  {path}")
            
            return paths
        return None
    except Exception as e:
        print(f"获取路由时出错: {e}")
        return None

def check_llm_providers_route():
    """检查LLM供应商路由是否注册"""
    print("\n" + "=" * 60)
    print("检查LLM供应商路由")
    print("=" * 60)
    
    # 首先登录获取令牌
    login_url = f"{BASE_URL}/api/v1/auth/login"
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get("data", {}).get("access_token") if "data" in data else data.get("access_token")
            
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                
                # 测试各种可能的端点
                endpoints = [
                    "/api/v1/llm-providers",
                    "/api/v1/llm/providers",
                    "/api/v1/admin/llm-providers",
                    "/api/v1/llm",
                ]
                
                for endpoint in endpoints:
                    url = f"{BASE_URL}{endpoint}"
                    response = requests.get(url, headers=headers)
                    print(f"{endpoint}: {response.status_code}")
                    if response.status_code < 300:
                        print(f"  成功! 响应长度: {len(response.text)}")
                    elif response.status_code == 404:
                        print(f"  404 - 未找到")
                    else:
                        print(f"  错误: {response.text[:100]}")
            else:
                print("无法获取令牌")
        else:
            print(f"登录失败: {response.status_code}")
    except Exception as e:
        print(f"检查路由时出错: {e}")

def main():
    print("=" * 60)
    print("检查FastAPI路由注册状态")
    print("=" * 60)
    
    # 检查健康端点
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        print(f"健康检查: {response.status_code}")
        if response.status_code == 200:
            print(f"  响应: {response.json()}")
    except Exception as e:
        print(f"健康检查失败: {e}")
    
    # 获取已注册的路由
    get_registered_routes()
    
    # 专门检查LLM供应商路由
    check_llm_providers_route()

if __name__ == "__main__":
    main()