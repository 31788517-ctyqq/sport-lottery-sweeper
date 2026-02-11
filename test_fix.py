#!/usr/bin/env python3
"""
测试修复后的登录和LLM提供者端点
"""
import sys
import os
import requests
import json
import time

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
LLM_PROVIDERS_URL = f"{BASE_URL}/api/v1/llm-providers/"

def test_login():
    """测试登录端点"""
    print("Testing login endpoint...")
    payload = {
        "username": "admin",
        "password": "admin123"
    }
    try:
        resp = requests.post(LOGIN_URL, json=payload, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response body: {resp.text}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Login successful. Access token obtained.")
            print(f"Data keys: {data.keys()}")
            token = data.get("data", {}).get("access_token")
            if token:
                print(f"Token length: {len(token)}")
            else:
                print("No access_token in response data!")
            return token
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_llm_provider_create(token):
    """测试LLM提供者创建端点"""
    print("\nTesting LLM provider creation...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    import uuid
    unique_name = f"Test LLM Provider {uuid.uuid4().hex[:8]}"
    payload = {
        "name": unique_name,
        "provider_type": "openai",
        "api_key": "sk-test123",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo",
        "max_tokens": 2048,
        "temperature": 0.7,
        "timeout": 30,
        "enabled": True,
        "priority": 1,
        "config": {}
    }
    try:
        resp = requests.post(LLM_PROVIDERS_URL, json=payload, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        if resp.status_code == 201:
            print("LLM provider created successfully.")
            return True
        else:
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("Starting test...")
    # 首先尝试登录
    token = test_login()
    if not token:
        print("Login failed. Cannot proceed.")
        sys.exit(1)
    
    # 测试LLM提供者创建
    success = test_llm_provider_create(token)
    if success:
        print("\nAll tests passed!")
    else:
        print("\nLLM provider creation failed. Check the error above.")
        sys.exit(1)

if __name__ == "__main__":
    main()