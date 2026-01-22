"""
测试认证端点是否正常工作
"""
import requests
import json

# 测试URL
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"

print(f"测试目标: {LOGIN_URL}")
print("="*60)

# 测试1: 检查后端是否运行
print("\n[测试1] 检查后端健康状态...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"✓ 后端运行中: {response.json()}")
except Exception as e:
    print(f"✗ 后端无法访问: {e}")
    exit(1)

# 测试2: 检查API文档
print("\n[测试2] 检查API文档...")
try:
    response = requests.get(f"{BASE_URL}/docs", timeout=5)
    if response.status_code == 200:
        print(f"✓ API文档可访问: {BASE_URL}/docs")
    else:
        print(f"! API文档状态码: {response.status_code}")
except Exception as e:
    print(f"✗ API文档访问失败: {e}")

# 测试3: 检查OpenAPI规范中的路由
print("\n[测试3] 获取所有API路由...")
try:
    response = requests.get(f"{BASE_URL}/api/v1/openapi.json", timeout=5)
    if response.status_code == 200:
        openapi = response.json()
        paths = openapi.get('paths', {})
        auth_paths = {k: v for k, v in paths.items() if 'auth' in k}
        print(f"✓ 找到 {len(auth_paths)} 个认证相关路由:")
        for path in auth_paths:
            print(f"  - {path}")
    else:
        print(f"! OpenAPI状态码: {response.status_code}")
except Exception as e:
    print(f"✗ 获取路由失败: {e}")

# 测试4: 尝试登录请求
print(f"\n[测试4] 测试登录请求: POST {LOGIN_URL}")
try:
    payload = {
        "username": "admin",
        "password": "admin123"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"请求数据: {json.dumps(payload, indent=2)}")
    response = requests.post(LOGIN_URL, json=payload, headers=headers, timeout=5)
    
    print(f"\n响应状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"\n响应内容:")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)
        
    if response.status_code == 200:
        print("\n✓ 登录测试成功!")
    else:
        print(f"\n✗ 登录测试失败: {response.status_code}")
        
except Exception as e:
    print(f"✗ 登录请求失败: {e}")

print("\n" + "="*60)
print("测试完成")
