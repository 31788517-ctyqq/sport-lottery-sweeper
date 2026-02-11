import requests

# 获取认证token
auth_resp = requests.post('http://localhost:8000/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
print(f'Login status: {auth_resp.status_code}')

if auth_resp.status_code == 200:
    token = auth_resp.json()['data']['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试日志统计API
    stats_resp = requests.get('http://localhost:8000/api/v1/admin/system/logs/db/statistics', headers=headers)
    print(f'Stats status: {stats_resp.status_code}')
    if stats_resp.status_code == 200:
        stats_data = stats_resp.json()
        print(f'Full response: {stats_data}')
        print(f'Total logs exists: {"total_logs" in stats_data}')
        print(f'Logs by level exists: {"logs_by_level" in stats_data}')
        print(f'Logs by module exists: {"logs_by_module" in stats_data}')
    else:
        print(f'Stats error: {stats_resp.text}')
else:
    print('Login failed')