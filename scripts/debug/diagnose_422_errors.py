#!/usr/bin/env python3
"""
诊断422错误的具体原因
"""

import requests
import sys
import json

BASE_URL = "http://localhost:8001"
LOGIN_ENDPOINT = "/api/auth/login"
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "admin123"
TIMEOUT = 10

def get_token():
    """获取JWT令牌"""
    login_url = BASE_URL + LOGIN_ENDPOINT
    payload = {
        "username": LOGIN_USERNAME,
        "password": LOGIN_PASSWORD
    }
    
    try:
        response = requests.post(login_url, json=payload, timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "access_token" in data["data"]:
                token = data["data"]["access_token"]
            elif "access_token" in data:
                token = data["access_token"]
            else:
                print("令牌未找到")
                return None
            
            return token
        else:
            print(f"登录失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"登录请求异常: {e}")
    
    return None

def diagnose_endpoint(endpoint, token):
    """诊断单个端点"""
    url = BASE_URL + endpoint
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n诊断端点: {endpoint}")
    print("-" * 60)
    
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 422:
            try:
                error_data = response.json()
                print("422错误详情:")
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
                
                # 分析错误类型
                if "detail" in error_data:
                    detail = error_data["detail"]
                    if isinstance(detail, list):
                        for err in detail:
                            if "msg" in err:
                                print(f"错误信息: {err['msg']}")
                            if "type" in err:
                                print(f"错误类型: {err['type']}")
                                if "int_parsing" in err['type']:
                                    print("  原因: 需要整数类型的路径参数")
                                elif "value_error" in err['type']:
                                    print("  原因: 参数值错误")
                    
            except:
                print(f"原始响应: {response.text[:500]}")
        
        elif response.status_code >= 400:
            print(f"响应摘要: {response.text[:200]}")
    
    except Exception as e:
        print(f"请求异常: {e}")

def main():
    # 读取422错误端点
    endpoints = []
    try:
        with open('auth_smoke_get_results_latest.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split('\t')
            if len(parts) >= 2 and parts[1] == '422':
                endpoints.append(parts[0])
    except FileNotFoundError:
        print("错误: 找不到测试结果文件")
        sys.exit(1)
    
    if not endpoints:
        print("未找到422错误端点")
        return
    
    print(f"发现 {len(endpoints)} 个422错误端点")
    
    # 获取令牌
    token = get_token()
    if not token:
        print("无法获取认证令牌")
        sys.exit(1)
    
    # 诊断前10个端点
    for i, endpoint in enumerate(endpoints[:10], 1):
        diagnose_endpoint(endpoint, token)
        
        # 稍微延迟，避免请求过快
        if i < len(endpoints[:10]):
            import time
            time.sleep(0.5)
    
    print(f"\n已诊断 {len(endpoints[:10])} 个端点 (共 {len(endpoints)} 个)")

if __name__ == "__main__":
    main()