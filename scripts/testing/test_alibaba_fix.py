import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_connection():
    """测试API连接"""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("[OK] 后端服务正在运行")
            return True
        else:
            print(f"[ERROR] 后端服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] 无法连接到后端服务: {e}")
        return False

def login():
    """获取管理员令牌"""
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"[OK] 登录成功，获取到令牌")
            return token
        else:
            print(f"[ERROR] 登录失败: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] 登录异常: {e}")
        return None

def get_providers(token):
    """获取现有供应商"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/llm-providers/", headers=headers, timeout=5)
        if response.status_code == 200:
            providers = response.json()
            print(f"[OK] 获取到 {len(providers)} 个供应商")
            return providers
        else:
            print(f"[ERROR] 获取供应商失败: {response.status_code}, {response.text}")
            return []
    except Exception as e:
        print(f"[ERROR] 获取供应商异常: {e}")
        return []

def test_provider_connection(token, provider_id):
    """测试指定供应商连接"""
    headers = {"Authorization": f"Bearer {token}"}
    test_data = {
        "test_prompt": "Hello, please respond with 'OK' to confirm connectivity.",
        "timeout_ms": 5000
    }
    try:
        response = requests.post(
            f"{BASE_URL}/llm-providers/{provider_id}/test",
            json=test_data,
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] 供应商测试结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result
        else:
            print(f"[ERROR] 供应商测试失败: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] 供应商测试异常: {e}")
        return None

def main():
    print("测试阿里云(alibaba)供应商连接修复...")
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(3)
    
    # 测试连接
    if not test_connection():
        return
    
    # 获取令牌
    token = login()
    if not token:
        return
    
    # 获取供应商列表
    providers = get_providers(token)
    if not providers:
        print("[INFO] 没有现有供应商，需要先创建")
        return
    
    # 查找阿里云供应商
    alibaba_providers = [p for p in providers if p.get("provider_type") in ["alibaba", "qwen"]]
    if not alibaba_providers:
        print("[INFO] 没有找到阿里云供应商，请先创建")
        return
    
    # 测试每个阿里云供应商
    for provider in alibaba_providers:
        print(f"\n测试供应商: {provider['name']} (类型: {provider['provider_type']})")
        result = test_provider_connection(token, provider['id'])
        
        if result:
            if result.get("success"):
                print(f"[SUCCESS] 供应商连接测试成功!")
            else:
                print(f"[FAILURE] 供应商连接测试失败: {result.get('message')}")
        else:
            print("[ERROR] 无法获取测试结果")

if __name__ == "__main__":
    main()