import requests
import sys

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
USER_LIST_URL = f"{BASE_URL}/api/v1/admin/admin-users/"

def test_user_list_api():
    # 1. 登录获取令牌
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    try:
        resp = requests.post(LOGIN_URL, json=login_data, timeout=10)
        resp.raise_for_status()
        token = resp.json().get("data", {}).get("access_token")
        if not token:
            print("ERROR: No access token in response")
            print(resp.json())
            return False
        print("Login successful")
    except Exception as e:
        print(f"ERROR: Login failed: {e}")
        return False
    
    # 2. 获取用户列表
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(USER_LIST_URL, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        print(f"User list API returned status {resp.status_code}")
        print(f"Response structure: {list(data.keys())}")
        if data.get("data"):
            items = data["data"].get("items", [])
            total = data["data"].get("total", 0)
            print(f"Total users: {total}, items: {len(items)}")
            if items:
                print(f"First user: {items[0].get('username')} ({items[0].get('email')})")
        else:
            print("No data field in response")
        return True
    except Exception as e:
        print(f"ERROR: User list API failed: {e}")
        print(f"Response: {resp.text if 'resp' in locals() else 'No response'}")
        return False

if __name__ == "__main__":
    print("Testing user list API...")
    success = test_user_list_api()
    sys.exit(0 if success else 1)