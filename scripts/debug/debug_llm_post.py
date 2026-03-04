#!/usr/bin/env python3
"""
调试 LLM 供应商创建 POST 请求的 500 错误
"""
import sys
import json
import requests
from pprint import pprint

# 配置
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
LLM_PROVIDERS_URL = f"{BASE_URL}/api/v1/llm-providers/"

def get_auth_token():
    """获取有效的 JWT 令牌"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print(f"正在登录 {LOGIN_URL}...")
    try:
        resp = requests.post(LOGIN_URL, json=login_data, timeout=10)
        print(f"登录状态码: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("access_token")
            if token:
                print(f"成功获取令牌 (长度: {len(token)})")
                return token
            else:
                print("响应中没有 access_token 字段")
                pprint(data)
        else:
            print(f"登录失败: {resp.status_code}")
            print(resp.text)
    except Exception as e:
        print(f"登录请求异常: {e}")
    
    return None

def test_llm_provider_create(token):
    """测试创建 LLM 供应商"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 使用与用户请求中类似的 payload
    payload = {
        "name": "测试供应商",
        "provider_type": "openai",
        "api_key": "sk-test123456789",
        "api_base": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo",
        "max_tokens": 2048,
        "temperature": 0.7,
        "timeout": 30,
        "max_retries": 3,
        "concurrent_limit": 5,
        "enabled": True,
        "priority": 1,
        "description": "测试供应商描述"
    }
    
    print(f"\n正在发送 POST 请求到 {LLM_PROVIDERS_URL}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        resp = requests.post(LLM_PROVIDERS_URL, json=payload, headers=headers, timeout=30)
        print(f"\n响应状态码: {resp.status_code}")
        print(f"响应头:")
        for key, value in resp.headers.items():
            print(f"  {key}: {value}")
        
        print(f"\n响应体:")
        try:
            error_data = resp.json()
            pprint(error_data)
        except:
            print(resp.text)
            
        # 如果是 500 错误，尝试获取更多调试信息
        if resp.status_code == 500:
            print("\n=== 500 错误详细信息 ===")
            # 尝试在开发环境中可能启用的调试端点
            debug_url = f"{BASE_URL}/api/v1/llm-providers/debug"
            try:
                debug_resp = requests.get(debug_url, headers=headers, timeout=5)
                if debug_resp.status_code == 200:
                    print("调试信息:")
                    pprint(debug_resp.json())
            except:
                pass
        
    except Exception as e:
        print(f"请求异常: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("=== 调试 LLM 供应商创建 500 错误 ===")
    
    # 1. 获取令牌
    token = get_auth_token()
    if not token:
        print("无法获取认证令牌，退出")
        sys.exit(1)
    
    # 2. 测试创建
    test_llm_provider_create(token)
    
    print("\n=== 调试完成 ===")

if __name__ == "__main__":
    main()