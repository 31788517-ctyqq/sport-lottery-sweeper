"""
测试API端点功能
"""
import requests
import json

BASE_URL = "http://localhost:8002/api/v1"

def test_login():
    """测试登录功能"""
    print("测试登录功能...")
    login_url = f"{BASE_URL}/auth/login"
    login_data = {
        "username": "sa_mock_data_2026_01_19",
        "password": "SuperAdmin@123456"
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            result = response.json()
            token = result.get('data', {}).get('access_token')
            print(f"✅ 登录成功，获取到token: {token[:20]}..." if token else "❌ 登录失败")
            return token
        else:
            print(f"❌ 登录失败，状态码: {response.status_code}, 响应: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def test_admin_users(token):
    """测试后台用户管理功能"""
    print("\n测试后台用户管理功能...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"{BASE_URL}/admin-users/"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 获取后台用户列表成功，共 {result.get('data', {}).get('total', 0)} 条记录")
            return True
        else:
            print(f"❌ 获取后台用户列表失败，状态码: {response.status_code}, 响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_frontend_users(token):
    """测试前台用户管理功能"""
    print("\n测试前台用户管理功能...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"{BASE_URL}/frontend-users/"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 获取前台用户列表成功，共 {result.get('data', {}).get('total', 0)} 条记录")
            return True
        else:
            print(f"❌ 获取前台用户列表失败，状态码: {response.status_code}, 响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def main():
    print("开始测试API功能...\n")
    
    # 测试登录
    token = test_login()
    
    if token:
        # 测试后台用户管理
        test_admin_users(token)
        
        # 测试前台用户管理
        test_frontend_users(token)
        
        print("\n🎉 所有测试完成！")
    else:
        print("\n❌ 登录失败，无法继续测试其他功能")

if __name__ == "__main__":
    main()