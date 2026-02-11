import requests
import json

BASE_URL = "http://localhost:8000"

def login():
    """使用admin账户登录获取token"""
    data = {
        "username": "admin",
        "password": "admin123"
    }
    try:
        resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json=data)
        resp.raise_for_status()
        result = resp.json()
        token = result.get("access_token") or result.get("token")
        print(f"登录成功，token: {token[:20]}...")
        return token
    except Exception as e:
        print(f"登录失败: {e}")
        return None

def test_statistics(token):
    """测试统计端点"""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "strength_filter": None,
        "win_pan_filter": None,
        "stability_filter": None,
        "p_level_filter": None,
        "leagues": None,
        "date_time": "26011",
        "date_range": None,
        "sort_by": "p_level",
        "sort_order": "desc",
        "include_derating": True
    }
    try:
        resp = requests.post(f"{BASE_URL}/api/v1/beidan-filter/statistics", headers=headers, json=payload)
        print(f"状态码: {resp.status_code}")
        if resp.status_code == 200:
            print("成功！响应:", json.dumps(resp.json(), ensure_ascii=False, indent=2))
        else:
            print(f"错误: {resp.text}")
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    token = login()
    if token:
        test_statistics(token)
    else:
        print("无法获取token，退出")