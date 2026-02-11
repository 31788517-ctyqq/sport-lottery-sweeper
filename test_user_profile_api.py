import requests
import json
from datetime import datetime, timedelta
import jwt
from backend.config import settings

def generate_test_token():
    payload = {
        'user_id': 1,
        'username': 'admin',
        'role': 'admin',
        'user_type': 'admin',
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

def test_api_endpoints():
    base_url = 'http://localhost:8000/api/v1/admin'
    token = generate_test_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    print('测试用户个人资料相关API端点...')

    # 测试获取当前用户信息
    try:
        response = requests.get(f'{base_url}/admin-users/current-user', headers=headers)
        print(f'✓ 获取当前用户信息 - 状态码: {response.status_code}')
        if response.status_code == 200:
            print('  ✓ 获取当前用户信息成功')
        else:
            print(f'  ✗ 获取当前用户信息失败: {response.text}')
    except Exception as e:
        print(f'  ✗ 获取当前用户信息错误: {e}')

    # 测试获取登录历史
    try:
        response = requests.get(f'{base_url}/admin-users/login-history', headers=headers, params={'limit': 10})
        print(f'✓ 获取登录历史 - 状态码: {response.status_code}')
        if response.status_code == 200:
            print('  ✓ 获取登录历史成功')
        else:
            print(f'  ✗ 获取登录历史失败: {response.text}')
    except Exception as e:
        print(f'  ✗ 获取登录历史错误: {e}')

    # 测试获取统计信息
    try:
        response = requests.get(f'{base_url}/admin-users/stats/overview', headers=headers)
        print(f'✓ 获取统计信息 - 状态码: {response.status_code}')
        if response.status_code == 200:
            print('  ✓ 获取统计信息成功')
        else:
            print(f'  ✗ 获取统计信息失败: {response.text}')
    except Exception as e:
        print(f'  ✗ 获取统计信息错误: {e}')

    # 测试修改密码端点
    try:
        response = requests.put(f'{base_url}/change-password', headers=headers, json={
            'old_password': 'old_password',
            'new_password': 'new_password',
            'confirm_password': 'new_password'
        })
        print(f'✓ 修改密码端点 - 状态码: {response.status_code}')
        if response.status_code in [200, 400]:  # 200表示成功，400表示参数错误但端点存在
            print('  ✓ 修改密码端点存在')
        else:
            print(f'  ✗ 修改密码端点失败: {response.text}')
    except Exception as e:
        print(f'  ✗ 修改密码端点错误: {e}')

if __name__ == "__main__":
    test_api_endpoints()