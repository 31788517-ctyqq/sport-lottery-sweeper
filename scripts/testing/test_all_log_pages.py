import requests
import json

base_url = 'http://localhost:8001'

# 测试各个日志API端点
log_types = ['system', 'user', 'security', 'api']

for log_type in log_types:
    url = f'{base_url}/api/v1/admin/system/logs/db/{log_type}?skip=0&limit=5'
    response = requests.get(url)
    print(f'=== {log_type.title()} Logs API Response ===')
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Response type: {type(data)}')
        if isinstance(data, list):
            print(f'Number of logs returned: {len(data)}')
            if data:
                print(f'First log keys: {list(data[0].keys())}')
        elif isinstance(data, dict):
            print(f'Response keys: {list(data.keys())}')
            if 'items' in data:
                print(f'Items count: {len(data["items"])}')
            else:
                print('No items key in response')
    else:
        print(f'Error: {response.text}')
    print()