import requests
import json

base_url = 'http://localhost:8001'

# 测试统计数据
stats_url = f'{base_url}/api/v1/admin/system/logs/db/statistics'
response = requests.get(stats_url)
print('=== Statistics API Response ===')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Total logs: {data["total_logs"]}')
    print(f'Logs by level: {data["logs_by_level"]}')
    print(f'Logs by module: {data["logs_by_module"]}')

print()

# 测试用户日志
user_url = f'{base_url}/api/v1/admin/system/logs/db/user?skip=0&limit=5'
response = requests.get(user_url)
print('=== User Logs API Response ===')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Type: {type(data)}')
    print(f'Count: {len(data)}')
    if data:
        print(f'First item: {json.dumps(data[0], indent=2)[:200]}...')

print()

# 测试安全日志
security_url = f'{base_url}/api/v1/admin/system/logs/db/security?skip=0&limit=5'
response = requests.get(security_url)
print('=== Security Logs API Response ===')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Type: {type(data)}')
    print(f'Count: {len(data)}')
    if data:
        print(f'First item: {json.dumps(data[0], indent=2)[:200]}...')

print()

# 测试API日志
api_url = f'{base_url}/api/v1/admin/system/logs/db/api?skip=0&limit=5'
response = requests.get(api_url)
print('=== API Logs API Response ===')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Type: {type(data)}')
    print(f'Count: {len(data)}')
    if data:
        print(f'First item: {json.dumps(data[0], indent=2)[:200]}...')