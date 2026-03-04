import requests
import sys

def test_login(endpoint, username, password):
    url = f"http://localhost:8000{endpoint}"
    data = {"username": username, "password": password}
    
    print(f"\n测试端点: {endpoint}")
    print(f"用户名: {username}")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("成功: 登录成功!")
            result = response.json()
            print(f"响应代码: {result.get('code')}")
            print(f"消息: {result.get('message')}")
            return True
        else:
            print(f"失败: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到后端服务")
        return False
    except Exception as e:
        print(f"错误: {e}")
        return False

def main():
    print("=== 测试两个登录端点 ===")
    
    # 测试普通用户登录端点
    user_success = test_login("/api/v1/auth/login", "admin", "admin123")
    
    # 测试管理员登录端点  
    admin_success = test_login("/api/v1/admin/login", "admin", "admin123")
    
    print("\n=== 总结 ===")
    print(f"普通用户登录: {'成功' if user_success else '失败'}")
    print(f"管理员登录: {'成功' if admin_success else '失败'}")
    
    # 建议
    if user_success and not admin_success:
        print("\n分析: 普通用户登录成功，但管理员登录失败。")
        print("可能原因: admin用户存在于users表而非admin_users表。")
        print("解决方案: 在admin_users表中创建管理员账户，或修改/admin/login端点逻辑。")
    elif not user_success and admin_success:
        print("\n分析: 管理员登录成功，但普通用户登录失败。")
        print("可能原因: admin用户可能只在admin_users表中。")
    elif user_success and admin_success:
        print("\n分析: 两个端点都登录成功。")
        print("注意: 两个端点可能都查询相同的表。")
    else:
        print("\n分析: 两个登录都失败。")
        print("可能原因: 用户名/密码错误，或后端服务未运行。")

if __name__ == "__main__":
    main()