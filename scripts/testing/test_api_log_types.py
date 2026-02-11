import requests
import json

response = requests.get('http://localhost:8001/api/v1/admin/system/logs/db/api?skip=0&limit=1')
if response.status_code == 200:
    data = response.json()
    if data and len(data) > 0:
        log_entry = data[0]
        print('API日志字段类型验证：')
        print(f'- id: {type(log_entry.get("id"))} (应为int)')
        print(f'- timestamp: {type(log_entry.get("timestamp"))} (应为str)')
        print(f'- level: {type(log_entry.get("level"))} (应为str)')
        print(f'- module: {type(log_entry.get("module"))} (应为str)')
        print(f'- message: {type(log_entry.get("message"))} (应为str)')
        print(f'- request_path: {type(log_entry.get("request_path"))} (应为str)')
        print(f'- response_status: {type(log_entry.get("response_status"))} (应为int)')
        print(f'- duration_ms: {type(log_entry.get("duration_ms"))} (应为int)')
        print(f'- extra_data: {type(log_entry.get("extra_data"))} (应为str)')
        print()
        print('字段值示例：')
        print(f'- id: {log_entry.get("id")}')
        print(f'- timestamp: {log_entry.get("timestamp")}')
        print(f'- level: {log_entry.get("level")}')
        print(f'- module: {log_entry.get("module")}')
        print(f'- message: {log_entry.get("message")}')
        print(f'- request_path: {log_entry.get("request_path")}')
        print(f'- response_status: {log_entry.get("response_status")}')
        print(f'- duration_ms: {log_entry.get("duration_ms")}')
        print(f'- extra_data (部分): {log_entry.get("extra_data")[:100]}...')
    else:
        print('没有获取到数据')
else:
    print(f'API请求失败: {response.status_code}')
    print(response.text[:500])