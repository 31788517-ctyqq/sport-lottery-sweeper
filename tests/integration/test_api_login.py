import requests

def test_login_api():
    url = "http://localhost:8001/api/v1/auth/login"  # 使用正确的端口
    
    # 测试数据
    payload = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("正在尝试登录...")
        print(f"请求URL: {url}")
        print(f"请求数据: {payload}")
        
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                print("\n[OK] 登录成功!")
                print(f"访问令牌: {data.get('data', {}).get('access_token', '')[:20]}...")
                print(f"用户信息: {data.get('data', {}).get('user_info', {})}")
            else:
                print(f"\n[ERROR] 登录失败: {data.get('message', '未知错误')}")
        else:
            print(f"\n[ERROR] 请求失败: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] 请求过程中发生错误: {str(e)}")

if __name__ == "__main__":
    test_login_api()