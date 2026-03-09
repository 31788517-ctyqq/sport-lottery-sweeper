import requests
import json
import sys

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"

def get_token():
    """获取JWT令牌"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    try:
        resp = requests.post(LOGIN_URL, json=login_data, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # 响应结构可能是 {"data": {"access_token": "..."}}
        if "data" in data and "access_token" in data["data"]:
            token = data["data"]["access_token"]
            return token
        elif "access_token" in data:
            token = data["access_token"]
            return token
        else:
            print(f"登录响应中没有找到令牌: {data}")
            return None
    except Exception as e:
        print(f"登录失败: {e}")
        return None

def test_endpoint(endpoint, token):
    """测试特定端点"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"}
    print(f"\n测试端点: {endpoint}")
    print(f"URL: {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        print(f"状态码: {resp.status_code}")
        if resp.status_code != 200:
            print(f"响应体: {resp.text[:500]}")
        else:
            print(f"响应体: {resp.text[:200]}...")
        # 尝试解析JSON以获取更详细的错误信息
        if resp.status_code == 500:
            try:
                error_data = resp.json()
                print(f"错误JSON: {json.dumps(error_data, indent=2)}")
            except:
                pass
    except Exception as e:
        print(f"请求异常: {e}")

def main():
    token = get_token()
    if not token:
        print("无法获取令牌，退出")
        sys.exit(1)
    
    print(f"令牌获取成功: {token[:50]}...")
    
    # 测试北单比赛端点
    test_endpoint("/api/v1/admin/matches/beidan/matches", token)
    
    # 测试监控概览端点
    test_endpoint("/api/v1/monitoring/dashboard/overview", token)

if __name__ == "__main__":
    main()