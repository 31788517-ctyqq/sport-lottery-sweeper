import requests
import json

# 测试不同的API端点
api_endpoints = [
    '/api/v1/admin/logs/system/logs/db/statistics',
    '/api/v1/admin/system/logs/db/statistics',
    '/api/v1/admin/logs/db/statistics',
    '/api/v1/admin/logs/system',
    '/api/v1/admin/logs',
    '/api/admin/system/logs/db/statistics'
]

print("正在测试日志API端点...")
print("="*60)

for endpoint in api_endpoints:
    try:
        response = requests.get(f'http://localhost:8001{endpoint}', timeout=5)
        print(f"{endpoint:<45} -> {response.status_code} ({'SUCCESS' if response.status_code == 200 else 'FAILED'})")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  Response preview: {json.dumps(data, ensure_ascii=False)[:100]}...")
            except:
                print(f"  Non-JSON response: {response.text[:100]}...")
        elif response.status_code != 404:
            print(f"  Error response: {response.text[:100]}...")
    except requests.exceptions.ConnectionError:
        print(f"{endpoint:<45} -> Connection Error")
    except Exception as e:
        print(f"{endpoint:<45} -> Exception: {str(e)}")
    print("-" * 60)

print("\n测试完成")