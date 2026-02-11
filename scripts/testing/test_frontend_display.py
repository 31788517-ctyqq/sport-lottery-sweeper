import requests
import json

# 测试API端点返回的数据格式
base_url = "http://localhost:8001"

print("Testing API response format for frontend display...")

# 测试统计数据API
stats_url = f"{base_url}/api/v1/admin/system/logs/db/statistics"
stats_response = requests.get(stats_url)
print(f"\nStatistics API ({stats_url}):")
print(f"Status: {stats_response.status_code}")
if stats_response.status_code == 200:
    stats_data = stats_response.json()
    print(f"Total logs: {stats_data.get('total_logs', 'N/A')}")
    print(f"Sample data: {json.dumps(stats_data, indent=2)[:200]}...")

# 测试系统日志API
system_url = f"{base_url}/api/v1/admin/system/logs/db/system?skip=0&limit=5"
system_response = requests.get(system_url)
print(f"\nSystem logs API ({system_url}):")
print(f"Status: {system_response.status_code}")
if system_response.status_code == 200:
    system_data = system_response.json()
    print(f"Response type: {type(system_data)}")
    if isinstance(system_data, list) and len(system_data) > 0:
        print(f"Number of logs returned: {len(system_data)}")
        print(f"First log keys: {list(system_data[0].keys())}")
        print(f"Sample log: {json.dumps(system_data[0], indent=2)[:200]}...")
    elif isinstance(system_data, dict):
        print(f"Response keys: {list(system_data.keys())}")
        if 'items' in system_data:
            print(f"Number of items: {len(system_data['items'])}")
        else:
            print("No 'items' key in response")
    else:
        print(f"Unexpected response format: {system_data}")

print("\nTest completed.")