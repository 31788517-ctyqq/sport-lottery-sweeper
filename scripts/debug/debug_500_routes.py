#!/usr/bin/env python3
"""
调试500错误路由
"""
import requests
import sys

BASE_URL = "http://localhost:8001"
LOGIN_ENDPOINT = "/api/auth/login"
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "admin123"

def get_token():
    """获取JWT令牌"""
    login_url = BASE_URL + LOGIN_ENDPOINT
    payload = {
        "username": LOGIN_USERNAME,
        "password": LOGIN_PASSWORD
    }
    
    try:
        response = requests.post(login_url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # 令牌在 data.access_token 中
            if "data" in data and "access_token" in data["data"]:
                token = data["data"]["access_token"]
                return token
            elif "access_token" in data:
                token = data["access_token"]
                return token
            else:
                print("令牌未找到，响应结构:", data.keys())
        else:
            print(f"登录失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"登录请求异常: {e}")
    return None

def test_route(route, token):
    """测试单个路由"""
    url = BASE_URL + route
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"路由: {route}")
        print(f"状态码: {response.status_code}")
        if response.status_code == 500:
            print(f"错误详情: {response.text[:1000]}")
        else:
            print(f"响应摘要: {response.text[:200]}")
        print("-" * 50)
    except Exception as e:
        print(f"请求异常: {e}")

def main():
    # 从冒烟测试结果中提取500错误路由
    routes_500 = [
        "/api/v1/admin/matches/beidan/matches",
        "/api/v1/admin/matches/jingcai/matches",
        "/api/v1/admin/matches/league/config",
        "/api/v1/admin/matches/leagues",
        "/api/v1/admin/options",
        "/api/v1/admin/stats",
        "/api/v1/admin/user-profiles/",
        "/api/v1/admin/user-profiles/{user_id}",
        "/api/v1/admin/users/",
        "/api/v1/admin/users/admin",
        "/api/v1/admin/users/profile",
        "/api/v1/beidan-schedules/",
        "/api/v1/beidan-schedules/stats",
        "/api/v1/companies/all",
        "/api/v1/crawler-alert/records",
        "/api/v1/crawler-alert/rules",
        "/api/v1/crawler-alert/stats",
        "/api/v1/leagues/leagues/stats",
        "/api/v1/metrics/metrics/api-performance",
        "/api/v1/metrics/metrics/errors",
        "/api/v1/metrics/metrics/system",
        "/api/v1/monitoring/dashboard/alert-trends",
        "/api/v1/monitoring/dashboard/overview",
        "/api/v1/monitoring/dashboard/realtime-metrics",
        "/api/v1/monitoring/dashboard/source-performance",
        "/api/v1/monitoring/dashboard/top-issues",
        "/api/v1/odds/odds/anomalies",
        "/api/v1/odds/odds/monitoring",
        "/api/v1/odds/odds/stats",
        "/api/v1/users/",
        "/api/v1/users/admin",
        "/api/v1/users/profile",
        "/api/v1/lottery-schedules/lottery-schedules/",
        "/api/v1/lottery-schedules/lottery-schedules/stats",
    ]
    
    token = get_token()
    if not token:
        print("无法获取令牌，退出")
        sys.exit(1)
    
    print(f"令牌获取成功，开始测试{len(routes_500)}个路由...")
    
    for route in routes_500:
        test_route(route, token)

if __name__ == "__main__":
    main()