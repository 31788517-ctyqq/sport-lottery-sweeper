#!/usr/bin/env python3
"""
直接测试500错误路由，使用admin123密码
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"

def get_token():
    """获取JWT令牌"""
    payload = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=payload, timeout=10)
        print(f"登录状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            token = data["data"]["access_token"]
            print(f"令牌获取成功: {token[:50]}...")
            return token
        else:
            print(f"登录失败: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"登录异常: {e}")
        return None

def test_route(route, token):
    """测试单个路由"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}{route}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"\n测试路由: {route}")
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 500:
            print(f"  500错误详情:")
            print(f"    响应头: {dict(response.headers)}")
            if response.text:
                print(f"    响应正文 (前500字符):")
                print(f"      {response.text[:500]}")
                try:
                    error_data = response.json()
                    print(f"    JSON解析:")
                    print(f"      {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                except:
                    pass
        elif response.status_code == 200:
            print(f"  成功!")
        else:
            print(f"  其他状态码，响应: {response.text[:200]}")
            
        return response.status_code
    except Exception as e:
        print(f"  请求异常: {e}")
        return 0

def main():
    print("开始调试500错误路由...")
    
    # 获取令牌
    token = get_token()
    if not token:
        print("无法获取令牌，退出")
        return
    
    # 从结果文件中读取500错误路由
    with open("auth_smoke_get_results.txt", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    error_500_routes = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and '\t' in line:
            route, status = line.split('\t', 1)
            if status == '500':
                error_500_routes.append(route)
    
    print(f"\n找到 {len(error_500_routes)} 个500错误路由")
    
    # 测试前5个路由
    for i, route in enumerate(error_500_routes[:5]):
        print(f"\n{i+1}. 测试: {route}")
        test_route(route, token)
        time.sleep(0.5)
    
    print("\n调试完成")

if __name__ == "__main__":
    main()