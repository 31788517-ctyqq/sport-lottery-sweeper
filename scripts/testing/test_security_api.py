import requests
import json

# 首先登录获取令牌
try:
    login_data = {'username': 'admin', 'password': 'admin123'}
    login_response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)
    
    if login_response.status_code == 200 and login_response.json()['code'] == 200:
        token = login_response.json()['data']['access_token']
        print('成功获取令牌')
        
        # 使用令牌访问安全日志API
        headers = {'Authorization': f'Bearer {token}'}
        logs_response = requests.get(
            'http://localhost:8000/api/v1/admin/system/logs/db/security?page=1&size=20',
            headers=headers
        )
        
        print(f'使用认证访问状态码: {logs_response.status_code}')
        if logs_response.status_code == 200:
            data = logs_response.json()
            print(f'API响应数据结构: {type(data)}')
            print(f'API响应内容: {data}')
        else:
            print(f'访问失败: {logs_response.text}')
    else:
        print(f'登录失败: {login_response.text}')
        
except Exception as e:
    print(f'错误: {e}')