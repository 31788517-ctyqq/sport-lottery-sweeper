import requests
import json

# 登录获取token
login_response = requests.post('http://localhost:8000/api/v1/auth/login', 
                              json={'username': 'admin', 'password': 'admin123'})
token = login_response.json()['data']['access_token']
print(f'Login successful, token: {token[:20]}...')

# 添加测试数据源
source_data = {
    'name': '竞彩足球官方API',
    'type': 'api',
    'url': 'https://api.sports.com/football',
    'config': '{\"category\": \"football\", \"timeout\": 30}',
    'status': True
}

create_response = requests.post('http://localhost:8000/api/v1/admin/sources',
                               headers={'Authorization': f'Bearer {token}'},
                               json=source_data)

print('Create Status:', create_response.status_code)
print('Create Response:', create_response.json())

# 查询数据源列表
list_response = requests.get('http://localhost:8000/api/v1/admin/sources',
                            headers={'Authorization': f'Bearer {token}'})

print('List Status:', list_response.status_code)
print('List Response:', list_response.json())
