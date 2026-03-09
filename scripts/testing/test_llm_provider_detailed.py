#!/usr/bin/env python3
"""
详细测试LLM供应商创建API
"""
import requests
import json
import sys
import traceback

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
CREATE_URL = f"{BASE_URL}/api/v1/llm-providers/"

def get_token():
    """获取JWT令牌"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    try:
        response = requests.post(LOGIN_URL, json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("access_token")
        else:
            print(f"登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"登录请求异常: {e}")
        return None

def test_create_provider(token):
    """测试创建LLM供应商"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    provider_data = {
        "name": "测试供应商-" + str(hash(token) % 1000),
        "provider_type": "openai",
        "description": "这是一个测试供应商",
        "api_key": "sk-test123456789",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-3.5-turbo",
        "available_models": ["gpt-3.5-turbo", "gpt-4"],
        "enabled": True,
        "priority": 1,
        "max_requests_per_minute": 60,
        "timeout_seconds": 30,
        "cost_per_token": {
            "input": 0.0015,
            "output": 0.002
        },
        "rate_limit_strategy": "token_bucket",
        "retry_policy": {
            "max_retries": 3,
            "backoff_factor": 2
        },
        "circuit_breaker_config": {
            "failure_threshold": 5,
            "reset_timeout": 60
        },
        "version": "1.0.0",
        "tags": ["测试", "openai"]
    }
    
    print(f"请求URL: {CREATE_URL}")
    print(f"请求头: {headers}")
    print(f"请求体: {json.dumps(provider_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(CREATE_URL, json=provider_data, headers=headers, timeout=10)
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应头:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        print(f"\n响应体:")
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            print(response.text)
        
        if response.status_code == 201:
            print("\n✅ LLM供应商创建成功")
            return True
        else:
            print("\n❌ LLM供应商创建失败")
            return False
    except Exception as e:
        print(f"\n创建请求异常: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始详细测试LLM供应商创建API...")
    
    # 获取令牌
    token = get_token()
    if not token:
        print("无法获取令牌，测试终止")
        sys.exit(1)
    
    print(f"令牌获取成功: {token[:20]}...")
    
    # 测试创建供应商
    success = test_create_provider(token)
    
    if success:
        print("\n✅ 所有测试通过")
        sys.exit(0)
    else:
        print("\n❌ 测试失败")
        sys.exit(1)