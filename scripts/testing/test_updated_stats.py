import requests
import json

base_url = 'http://localhost:8001'
stats_url = f'{base_url}/api/v1/admin/system/logs/db/statistics'
response = requests.get(stats_url)
print('=== Updated Statistics API Response ===')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Total logs: {data["total_logs"]}')
    print(f'Logs by level: {json.dumps(data["logs_by_level"], indent=2)}')
    print(f'Logs by module: {json.dumps(data["logs_by_module"], indent=2)}')
    
    # 检查特定类型的日志数量
    user_activities = data["logs_by_module"].get('user_operations', 0)
    security_events = data["logs_by_module"].get('security_events', 0)
    print(f'\nSpecific counts:')
    print(f'User activities: {user_activities}')
    print(f'Security events: {security_events}')