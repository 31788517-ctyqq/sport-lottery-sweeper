import requests
import sys

BASE_URL = "http://localhost:8001"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
BEIDAN_URL = f"{BASE_URL}/api/v1/admin/matches/beidan/matches"

def get_token():
    """获取JWT令牌"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        response.raise_for_status()
        data = response.json()
        if "data" in data and "access_token" in data["data"]:
            return data["data"]["access_token"]
        else:
            print(f"登录响应结构异常: {data}")
            return None
    except Exception as e:
        print(f"登录失败: {e}")
        return None

def test_beidan_endpoint(token):
    """测试北单比赛端点"""
    headers = {"Authorization": f"Bearer {token}"}
    params = {"days": 5}
    try:
        response = requests.get(BEIDAN_URL, headers=headers, params=params)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {response.headers}")
        try:
            print(f"响应体: {response.text[:500]}")
        except:
            print("无法读取响应体")
        if response.status_code == 500:
            print("500错误详情:", response.text[:1000])
        return response.status_code
    except Exception as e:
        print(f"请求异常: {e}")
        return None

if __name__ == "__main__":
    print("获取令牌...")
    token = get_token()
    if not token:
        print("无法获取令牌，退出")
        sys.exit(1)
    print("令牌获取成功")
    print("测试北单比赛端点...")
    status = test_beidan_endpoint(token)
    if status == 500:
        print("端点返回500内部服务器错误，需要检查后端日志。")