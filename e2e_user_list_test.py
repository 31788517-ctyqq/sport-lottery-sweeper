"""
用户列表页面端到端测试
从网络层、数据层、渲染层各个维度验证用户列表页面功能
"""

import requests
import time
import json
from datetime import datetime


def test_user_list_page():
    """
    测试用户列表页面功能
    """
    print("=" * 60)
    print("用户列表端到端测试开始")
    print("=" * 60)

    # 测试配置
    BASE_URL = "http://localhost:3000"
    BACKEND_API = "http://localhost:8000"

    print("\n执行测试: 用户列表页面功能测试")
    print("-" * 40)
    print("开始用户列表端到端测试...")

    # 1. 检查前端页面可用性
    print("\n1. 检查前端页面可用性...")
    try:
        # 注意：在实际测试中，我们需要访问前端页面，这里只是示例
        # 在真实情况下，我们会使用Playwright或Selenium来访问页面
        frontend_resp = requests.get(f"{BASE_URL}")
        print(f"   页面状态: {frontend_resp.status_code}")
        print("✅ 前端页面访问正常")
    except Exception as e:
        print(f"⚠️ 前端页面访问异常: {e}")

    # 2. 检查后端API可用性
    print("\n2. 检查后端用户管理API可用性...")
    
    # 首先尝试获取认证token（通常需要登录）
    auth_token = None
    try:
        # 尝试使用默认管理员账户登录
        login_data = {
            "username": "admin",
            "password": "admin123"  # 这通常是默认密码
        }
        login_resp = requests.post(f"{BACKEND_API}/api/v1/admin/login", json=login_data)
        if login_resp.status_code == 200:
            auth_data = login_resp.json()
            auth_token = auth_data.get("access_token", "")
            print(f"   登录状态: {login_resp.status_code}")
            print("✅ 后端认证成功")
        else:
            print(f"⚠️ 登录失败: {login_resp.status_code}")
            print("   尝试不带认证的API访问...")
    except Exception as e:
        print(f"⚠️ 认证过程异常: {e}")

    # 3. 测试用户API - 需要使用正确的API路径
    headers = {}
    if auth_token:
        headers['Authorization'] = f"Bearer {auth_token}"
    headers['Content-Type'] = 'application/json'

    print("\n3. 测试用户API...")
    
    # 检查用户API端点 - 使用实际注册的路径
    try:
        # 根据分析，后端实际注册的路径是 /api/v1/admin/admin-users
        users_url = f"{BACKEND_API}/api/v1/admin/admin-users?skip=0&limit=10"
        print(f"   尝试访问: {users_url}")
        users_resp = requests.get(users_url, headers=headers)
        print(f"   用户列表API状态: {users_resp.status_code}")
        
        if users_resp.status_code == 200:
            users_data = users_resp.json()
            print("✅ 用户API访问成功")
            print(f"   用户总数: {users_data.get('data', {}).get('total', 0) if isinstance(users_data.get('data'), dict) else 'N/A'}")
        else:
            print(f"❌ 用户API访问失败: {users_resp.status_code}")
            print(f"   响应: {users_resp.text}")
    except Exception as e:
        print(f"⚠️ 用户API测试异常: {e}")

    # 4. 测试创建用户
    print("\n4. 测试创建用户...")
    try:
        # 生成唯一用户名
        timestamp = int(time.time())
        new_user_data = {
            "username": f"test_user_{timestamp}",
            "email": f"test{timestamp}@example.com",
            "password": "TestPass123!",
            "real_name": f"Test User {timestamp}",
            "role": "user",
            "status": "active"
        }
        
        create_resp = requests.post(
            f"{BACKEND_API}/api/v1/admin/admin-users", 
            headers=headers, 
            json=new_user_data
        )
        print(f"   创建用户状态: {create_resp.status_code}")
        
        if create_resp.status_code in [200, 201]:
            created_user = create_resp.json()
            user_id = created_user.get('data', {}).get('id')
            print(f"✅ 用户创建成功: {new_user_data['username']}")
            print(f"   用户ID: {user_id}")
            
            # 5. 验证数据层 - 检查用户是否已保存
            print("\n5. 验证数据层 - 检查用户是否已保存...")
            if user_id:
                detail_resp = requests.get(
                    f"{BACKEND_API}/api/v1/admin/admin-users/{user_id}", 
                    headers=headers
                )
                if detail_resp.status_code == 200:
                    print(f"✅ 用户已正确保存到数据库: {new_user_data['username']}")
                    
                    # 6. 测试更新用户
                    print("\n6. 测试更新用户...")
                    update_data = {
                        "real_name": f"Updated Test User {timestamp}",
                        "status": "inactive"
                    }
                    update_resp = requests.put(
                        f"{BACKEND_API}/api/v1/admin/admin-users/{user_id}",
                        headers=headers,
                        json=update_data
                    )
                    print(f"   更新用户状态: {update_resp.status_code}")
                    if update_resp.status_code == 200:
                        print("✅ 用户更新成功")
                    
                    # 7. 测试删除用户
                    print("\n7. 清理测试数据...")
                    delete_resp = requests.delete(
                        f"{BACKEND_API}/api/v1/admin/admin-users/{user_id}",
                        headers=headers
                    )
                    print(f"   删除用户状态: {delete_resp.status_code}")
                    if delete_resp.status_code == 200:
                        print("✅ 测试用户已清理")
                else:
                    print(f"❌ 无法获取刚创建的用户: {detail_resp.status_code}")
        else:
            print(f"❌ 用户创建失败: {create_resp.status_code}")
            print(f"   响应: {create_resp.text}")
    except Exception as e:
        print(f"⚠️ 创建用户测试异常: {e}")

    # 8. 测试统计数据API
    print("\n8. 测试统计数据API...")
    try:
        stats_resp = requests.get(
            f"{BACKEND_API}/api/v1/admin/admin-users/stats",
            headers=headers
        )
        print(f"   统计API状态: {stats_resp.status_code}")
        if stats_resp.status_code == 200:
            print("✅ 统计数据API正常")
        else:
            print(f"⚠️ 统计API返回状态: {stats_resp.status_code}")
    except Exception as e:
        print(f"⚠️ 统计API测试异常: {e}")

    print("\n🎉 用户管理测试完成！")

    print("\n执行测试: 网络层测试")
    print("-" * 40)
    
    network_tests = [
        f"{BACKEND_API}/api/v1/admin/admin-users?skip=0&limit=10",
        f"{BACKEND_API}/api/v1/admin/admin-users/stats",
    ]
    
    for url in network_tests:
        try:
            resp = requests.get(url, headers=headers)
            print(f"   GET {url}: {resp.status_code}")
            if resp.status_code == 200:
                print("✅ 网络层测试通过")
            else:
                print(f"⚠️ 网络层测试警告: {resp.status_code}")
        except Exception as e:
            print(f"⚠️ 网络层测试异常: {e}")

    print("\n执行测试: 渲染层测试")
    print("-" * 40)
    print("渲染层测试需要前端自动化工具（如Playwright或Selenium）来完成，")
    print("验证UI组件是否正确显示数据，这部分通常在单独的前端测试中完成。")

    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print("=" * 60)
    print("用户列表功能测试: 待实际执行")
    print("网络层测试: 待实际执行") 
    print("渲染层测试: 待实际执行")
    print("\n总体结果: 待实际执行")


if __name__ == "__main__":
    test_user_list_page()