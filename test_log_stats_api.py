import requests

# 获取认证token
auth_resp = requests.post('http://localhost:8000/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
print(f'Login status: {auth_resp.status_code}')
print(f'Login response: {auth_resp.json()}')

if auth_resp.status_code == 200:
    token = auth_resp.json()['data']['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试日志统计API
    stats_resp = requests.get('http://localhost:8000/api/v1/admin/system/logs/db/statistics', headers=headers)
    print(f'Stats status: {stats_resp.status_code}')
    if stats_resp.status_code == 200:
        stats_data = stats_resp.json()
        print(f'Stats keys: {list(stats_data.keys())}')
        print(f'Total logs: {stats_data.get("total_logs", "missing")}')
        print(f'Logs by level: {stats_data.get("logs_by_level", "missing")}')
        print(f'Logs by module: {stats_data.get("logs_by_module", "missing")}')
    else:
        print(f'Stats error: {stats_resp.text}')
else:
    print('Login failed')